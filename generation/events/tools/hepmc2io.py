"""Minimal, dependency-free reader for HepMC2 IO_GenEvent ASCII files (HepMC 2.06, as written by
Pythia8ToHepMC / read by CMSSW_5_3 MCFileSource).  Streams one event at a time and keeps the raw
lines, so that tools can rewrite selected lines (vertex positions) and leave the rest byte-identical.

Format reminders (IO_GenEvent):
  E evnum nMPI scale aQCD aQED sig_id sig_vtx n_vtx beam1 beam2 n_rnd [rnd..] n_wgt [w..]
  U <momentum unit> <length unit>          (e.g. U GEV MM)
  V barcode id x y z t n_orphan n_out n_wgt [w..]
  P barcode pdg px py pz E m status theta phi endvtx_barcode n_flow [code idx ..]
A V line is followed by its n_orphan incoming orphan particles and then by its n_out outgoing
particles; a particle's production vertex is therefore the V line it is listed under (unless it is
one of the orphans), and its end vertex is given explicitly by endvtx_barcode (0 = none).
"""
import gzip

LEN_TO_MM = {'MM': 1.0, 'CM': 10.0}


def _open(path, mode='rt'):
    if str(path).endswith('.gz'):
        return gzip.open(path, mode, compresslevel=6) if 'w' in mode else gzip.open(path, mode)
    return open(path, mode)


class Vertex:
    __slots__ = ('bc', 'line', 'pos', 'pin', 'pout')

    def __init__(self, bc, line, pos):
        self.bc, self.line, self.pos = bc, line, pos   # pos = [x, y, z, t] in file units
        self.pin, self.pout = [], []                     # particle barcodes


class Particle:
    __slots__ = ('bc', 'pdg', 'p', 'm', 'status', 'prod', 'end')

    def __init__(self, bc, pdg, p, m, status, prod, end):
        self.bc, self.pdg, self.p, self.m, self.status, self.prod, self.end = bc, pdg, p, m, status, prod, end


class Event:
    """Raw lines + parsed graph.  vertices: {barcode: Vertex}, particles: {barcode: Particle}."""

    def __init__(self, lines, length_unit='MM'):
        self.lines = lines
        self.length_unit = length_unit
        self.vertices, self.particles = {}, {}
        self.number = None
        self._parse()

    def _parse(self):
        cur, n_orph, k = None, 0, 0
        for i, l in enumerate(self.lines):
            c = l[:1]
            if c == 'E':
                self.number = int(l.split()[1])
            elif c == 'U':
                self.length_unit = l.split()[2]
            elif c == 'V':
                f = l.split()
                bc = int(f[1])
                cur = Vertex(bc, i, [float(x) for x in f[3:7]])
                self.vertices[bc] = cur
                n_orph, k = int(f[7]), 0
            elif c == 'P':
                f = l.split()
                bc = int(f[1])
                end = int(f[11])
                prod = None
                if cur is not None:
                    if k < n_orph:                 # orphan: incoming to cur, no production vertex
                        pass
                    else:
                        prod = cur.bc
                        cur.pout.append(bc)
                    k += 1
                self.particles[bc] = Particle(bc, int(f[2]), [float(x) for x in f[3:7]], float(f[7]),
                                              int(f[8]), prod, end)
        for p in self.particles.values():
            if p.end and p.end in self.vertices:
                self.vertices[p.end].pin.append(p.bc)

    # ---- helpers -------------------------------------------------------------------------------
    def to_mm(self, v):
        return [x * LEN_TO_MM.get(self.length_unit, 1.0) for x in v]

    def descendant_vertices(self, vbc):
        """All vertices reachable downstream from vertex vbc (including vbc)."""
        out, stack = set(), [vbc]
        while stack:
            v = stack.pop()
            if v in out or v not in self.vertices:
                continue
            out.add(v)
            for pbc in self.vertices[v].pout:
                e = self.particles[pbc].end
                if e and e not in out:
                    stack.append(e)
        return out

    def lw_chains(self, pdg_abs=9000011):
        """[(top_particle, bottom_particle)] for each LW particle: top = first copy (mother not LW),
        bottom = last copy (its end vertex has no outgoing LW particle of the same id)."""
        res = []
        for p in self.particles.values():
            if abs(p.pdg) != pdg_abs:
                continue
            # top copy: production vertex has no incoming particle with the same pdg
            pv = self.vertices.get(p.prod)
            if pv is not None and any(self.particles[q].pdg == p.pdg for q in pv.pin):
                continue
            bot = p
            while True:
                ev = self.vertices.get(bot.end)
                if ev is None:
                    break
                nxt = [self.particles[q] for q in ev.pout if self.particles[q].pdg == bot.pdg]
                if not nxt:
                    break
                bot = nxt[0]
            res.append((p, bot))
        return res


def read_events(path):
    """Yield (header_lines, Event) ... header_lines is non-empty only for the first event; the
    trailing footer is yielded as (footer_lines, None)."""
    header, buf, unit = [], None, 'MM'
    with _open(path) as f:
        for l in f:
            if l.startswith('E '):
                if buf is not None:
                    yield header, Event(buf, unit)
                    header = []
                buf = [l]
            elif buf is None:
                header.append(l)
            elif l.startswith('HepMC::IO_GenEvent-END'):
                yield header, Event(buf, unit)
                buf = None
                header = [l]
            else:
                if l.startswith('U '):
                    unit = l.split()[2]
                buf.append(l)
        if buf is not None:
            yield header, Event(buf, unit)
            header = []
    yield header, None
