from math import cos, sin, tan, radians, degrees, atan2
from pygeom.geom3d import ihat, Coordinate, Vector
from .latticesection import LatticeSection
from .latticestrip import LatticeStrip

class LatticeSheet(object):
    sect1 = None
    sect2 = None
    bspc = None
    mirror = None
    levec = None
    cord = None
    strps = None
    pnls = None
    ctrls = None
    noload = None
    ruled = None
    width = None
    area = None
    def __init__(self, sect1: LatticeSection, sect2: LatticeSection):
        self.sect1 = sect1
        self.sect2 = sect2
        self.update()
    def update(self):
        if self.sect1.mirror or self.sect2.mirror:
            self.mirror = True
        else:
            self.mirror = False
        self.inherit_ruled()
        self.inherit_noload()
        self.inherit_spacing()
        self.inherit_controls()
        self.levec = self.sect2.pnt-self.sect1.pnt
        vecz = (ihat**self.levec).to_unit()
        vecy = (vecz**ihat).to_unit()
        self.cord = Coordinate(self.sect1.pnt, ihat, vecy, vecz)
        self.strps = []
        self.pnls = []
        self.width = self.levec*self.cord.diry
        self.area = self.width*(self.sect2.chord+self.sect1.chord)/2
    def mesh_strips(self, lsid: int):
        self.strps = []
        pnta = self.sect1.pnt
        vecr = self.levec
        crda = self.sect1.chord
        crdb = self.sect2.chord
        crdr = crdb-crda
        anga = self.sect1.twist
        angb = self.sect2.twist
        angr = angb-anga
        if self.ruled:
            radanga = radians(anga)
            cosanga = cos(radanga)
            sinanga = sin(radanga)
            xla = cosanga*crda
            zla = -sinanga*crda
            radangb = radians(angb)
            cosangb = cos(radangb)
            sinangb = sin(radangb)
            xlb = cosangb*crdb
            zlb = -sinangb*crdb
            xlr = xlb-xla
            zlr = zlb-zla
        cdoa = self.sect1.cdo
        cdob = self.sect2.cdo
        cdor = cdob-cdoa
        lenb = len(self.bspc)
        for i in range(lenb):
            bspc = self.bspc[i]
            bsp1 = bspc[0]
            bspm = bspc[1]
            bsp2 = bspc[2]
            pnt1 = pnta + bsp1*vecr
            pnt2 = pnta + bsp2*vecr
            pntm = pnta + bspm*vecr
            crd1 = crda + bsp1*crdr
            crd2 = crda + bsp2*crdr
            strp = LatticeStrip(lsid, pnt1, pnt2, crd1, crd2, bspc)
            if self.ruled:
                xl1 = xla + bsp1*xlr
                xl2 = xla + bsp2*xlr
                xlm = xla + bspm*xlr
                zl1 = zla + bsp1*zlr
                zl2 = zla + bsp2*zlr
                zlm = zla + bspm*zlr
                ang1 = degrees(atan2(-zl1, xl1))
                ang2 = degrees(atan2(-zl2, xl2))
                angm = degrees(atan2(-zlm, xlm))
            else:
                ang1 = anga+bsp1*angr
                ang2 = anga+bsp2*angr
                angm = anga+bspm*angr
            strp.set_twists(ang1, ang2)
            strp.set_twist(angm)
            cdo1 = cdoa + bsp1*cdor
            cdo2 = cdoa + bsp2*cdor
            strp.set_cdo(cdo1, cdo2)
            strp.sht = self
            self.strps.append(strp)
            lsid += 1
        return lsid
    def inherit_panels(self):
        self.pnls = []
        for strp in self.strps:
            for pnl in strp.pnls:
                self.pnls.append(pnl)
    def inherit_ruled(self):
        if self.mirror:
            self.ruled = self.sect2.ruled
        else:
            self.ruled = self.sect1.ruled
    def inherit_noload(self):
        if self.mirror:
            self.noload = self.sect2.noload
        else:
            self.noload = self.sect1.noload
    def inherit_spacing(self):
        if self.mirror:
            if self.sect2.bspc is None:
                self.bspc = [(0.0, 0.5, 1.0)]
            else:
                lenb = len(self.sect2.bspc)
                self.bspc = []
                for i in range(lenb):
                    blst = []
                    for j in range(2, -1, -1):
                        blst.append(1.0-self.sect2.bspc[i][j])
                    self.bspc.append(tuple(blst))
                self.bspc.reverse()
        else:
            if self.sect1.bspc is None:
                self.bspc = [(0.0, 0.5, 1.0)]
            else:
                self.bspc = self.sect1.bspc
    def inherit_controls(self):
        self.ctrls = {}
        if self.mirror:
            for control in self.sect2.ctrls:
                ctrl = self.sect2.ctrls[control]
                newctrl = ctrl.duplicate(mirror=True)
                self.ctrls[control] = newctrl
        else:
            for control in self.sect1.ctrls:
                ctrl = self.sect1.ctrls[control]
                newctrl = ctrl.duplicate(mirror=False)
                self.ctrls[control] = newctrl
        for control in self.ctrls:
            ctrl = self.ctrls[control]
            if ctrl.uhvec.return_magnitude() == 0.0:
                pnt1 = self.sect1.pnt
                crd1 = self.sect1.chord
                pnta = pnt1+crd1*ihat*ctrl.xhinge
                pnt2 = self.sect2.pnt
                crd2 = self.sect2.chord
                pntb = pnt2+crd2*ihat*ctrl.xhinge
                hvec = pntb-pnta
                ctrl.set_hinge_vector(hvec)
    def set_control_panels(self):
        for control in self.ctrls:
            ctrl = self.ctrls[control]
            for pnl in self.pnls:
                if pnl.cspc[3] >= ctrl.xhinge:
                    ctrl.add_panel(pnl)
    def set_strip_bpos(self):
        bpos = self.sect1.bpos
        for i, strp in enumerate(self.strps):
            bspc = self.bspc[i]
            strp.bpos = bpos+self.width*bspc[1]
    def __repr__(self):
        return '<LatticeSheet>'
