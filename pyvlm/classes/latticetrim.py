from time import time
from .latticeresult import LatticeResult, GammaResult
from .latticesystem import LatticeSystem
from numpy.matlib import zeros
from numpy.linalg import norm, inv
from math import degrees, radians

class LatticeTrim(LatticeResult):
    CLt = None
    CYt = None
    Clt = None
    Cmt = None
    Cnt = None
    def __init__(self, name: str, sys: LatticeSystem):
        super(LatticeTrim, self).__init__(name, sys)
    def set_targets(self, CLt: float=0.0, CYt: float=0.0,
                    Clt: float=0.0, Cmt: float=0.0, Cnt: float=0.0):
        self.CLt = CLt
        self.CYt = CYt
        self.Clt = Clt
        self.Cmt = Cmt
        self.Cnt = Cnt
    def delta_C(self):
        C = zeros((5, 1), dtype=float)
        C[0, 0] = self.CLt-self.nfres.CL
        C[1, 0] = self.CYt-self.nfres.CY
        C[2, 0] = self.Clt-self.nfres.Cl
        C[3, 0] = self.Cmt-self.nfres.Cm
        C[4, 0] = self.Cnt-self.nfres.Cn
        return C
    def target_Cmat(self):
        Ctgt = zeros((5, 1), dtype=float)
        Ctgt[0, 0] = self.CLt
        Ctgt[1, 0] = self.CYt
        Ctgt[2, 0] = self.Clt
        Ctgt[3, 0] = self.Cmt
        Ctgt[4, 0] = self.Cnt
        return Ctgt
    def current_Cmat(self):
        Ccur = zeros((5, 1), dtype=float)
        Ccur[0, 0] = self.nfres.CL
        Ccur[1, 0] = self.nfres.CY
        Ccur[2, 0] = self.nfres.Cl
        Ccur[3, 0] = self.nfres.Cm
        Ccur[4, 0] = self.nfres.Cn
        return Ccur
    def current_Dmat(self):
        numc = len(self.sys.ctrls)
        num = numc+2
        Dcur = zeros((num, 1), dtype=float)
        Dcur[0, 0] = radians(self.alpha)
        Dcur[1, 0] = radians(self.beta)
        c = 0
        for control in self.ctrls:
            Dcur[2+c, 0] = radians(self.ctrls[control])
            c += 1
        return Dcur
    def Hmat(self):
        numc = len(self.sys.ctrls)
        num = numc+2
        H = zeros((5, num), dtype=float)
        alres = GammaResult(self, self.galpha())
        H[0, 0] = alres.CL
        H[1, 0] = alres.CY
        H[2, 0] = alres.Cl
        H[3, 0] = alres.Cm
        H[4, 0] = alres.Cn
        btres = GammaResult(self, self.gbeta())
        H[0, 1] = btres.CL
        H[1, 1] = btres.CY
        H[2, 1] = btres.Cl
        H[3, 1] = btres.Cm
        H[4, 1] = btres.Cn
        ctgam = {}
        c = 0
        for control in self.ctrls:
            if self.ctrls[control] < 0.0:
                ctgam = self.gctrln_single(control)
            else:
                ctgam = self.gctrlp_single(control)
            ctres = GammaResult(self, ctgam)
            H[0, 2+c] = ctres.CL
            H[1, 2+c] = ctres.CY
            H[2, 2+c] = ctres.Cl
            H[3, 2+c] = ctres.Cm
            H[4, 2+c] = ctres.Cn
            c += 1
        return H
    def trim_iteration(self, crit: float=1e-6, imax: int=100):
        start = time()
        Ctgt = self.target_Cmat()
        Ccur = self.current_Cmat()
        Cdff = Ctgt-Ccur
        # nrmC = norm(Cdff)
        H = self.Hmat()
        # print(f'H = {H}')
        A = H.transpose()*H
        Ainv = inv(A)
        Dcur = self.current_Dmat()
        B = H.transpose()*Cdff
        Ddff = Ainv*B
        Dcur = Dcur+Ddff
        # i = 0
        # while nrmC > crit:
        #     B = H.transpose()*Cdff
        #     Ddff = Ainv*B
        #     Dcur = Dcur+Ddff
        #     Ccur = Ccur+H*Ddff
        #     Cdff = Ctgt-Ccur
        #     nrmC = norm(Cdff)
        #     print(f'normC = {nrmC}')
        #     i += 1
        #     if i >= imax:
        #         print('Convergence failed!')
        #         return False
        # print(f'Internal Iteration Counter = {i:d}')
        finish = time()
        elapsed = finish-start
        print(f'Trim Internal Iteration Duration = {elapsed:.3f} seconds.')
        return Dcur
    def trim(self, crit: float=1e-6, imax: int=100):
        Ctgt = self.target_Cmat()
        Ccur = self.current_Cmat()
        Cdff = Ctgt-Ccur
        nrmC = norm(Cdff)
        print(f'normC = {nrmC}')
        i = 0
        while nrmC > crit:
            print(f'Iteration {i:d}')
            Dcur = self.trim_iteration(crit, imax)
            if Dcur is False:
                return
            alpha = degrees(Dcur[0, 0])
            beta = degrees(Dcur[1, 0])
            ctrls = {}
            c = 0
            for control in self.ctrls:
                ctrls[control] = degrees(Dcur[2+c, 0])
                c += 1
            self.set_controls(**ctrls)
            self.set_state(alpha=alpha, beta=beta)
            Ccur = self.current_Cmat()
            Cdff = Ctgt-Ccur
            nrmC = norm(Cdff)
            print(f'alpha = {alpha:.6f} deg')
            print(f'beta = {beta:.6f} deg')
            for control in ctrls:
                print(f'{control} = {ctrls[control]:.6f} deg')
            print(f'normC = {nrmC}')
            i += 1
            if i >= imax:
                print('Convergence failed!')
                return False
    def to_result(self, name: str=''):
        if name == '':
            name = self.name
        res = LatticeResult(name, self.sys)
        res.rho = self.rho
        res.speed = self.speed
        res.alpha = self.alpha
        res.beta = self.beta
        res.pbo2V = self.pbo2V
        res.qco2V = self.qco2V
        res.rbo2V = self.rbo2V
        res.ctrls = self.ctrls
        res.rcg = self.rcg
        return res
