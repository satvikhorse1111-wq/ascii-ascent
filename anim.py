from __future__ import annotations

from sys import stdout
from clear import clear
from time import sleep
from utils import IOUtils
from maps import GameMap, LevelData
from typing import Callable, Iterator, Self
import pickle
import base64
from zlib import compress, decompress
from dataclasses import dataclass
from textwrap import fill

"""[ending.py] Contains the scene data for the ending scene
when the Tower level is beaten. Also contains
the ending function, which plays the scene using this data."""

type Pause = int | float
type StrFunc = Callable[[str], str]
type GameMapFunc = Callable[[GameMap], GameMap]

def IDENTITY[T](x: T) -> T:
    return x

DEFAULT_SPEED: bool = 1.0

@dataclass(frozen=True, slots=True)
class Line:

    text: str
    duration: Pause

    def __reduce__(self):

        return (self.__class__, (self.text, self.duration))

class Dialogue:

    def __init__(self, lines: Line) -> None:
        self.lines = lines

    def __iter__(self) -> Iterator[Line]:
        return iter(self.lines)

    @property
    def length(self):
        return sum(line.duration for line in self.lines)

    def run(self, *, text_func: StrFunc=IDENTITY, speed: bool=DEFAULT_SPEED
            ) -> None:

        for line in self:

            stdout.write(text_func(line.text) + "\n")
            sleep(line.duration / speed)

    def __reduce__(self):

        return (self.__class__, (self.lines,))

class Scene:

    def __init__(self,
                 display: GameMap,
                 pause: Pause=None,
                 dialogue: Dialogue=None
                 ) -> None:

        if pause is None and dialogue is None:
            raise ValueError("Must pass argument 'pause' or 'dialogue'")

        self.display = GameMap(display)
        self.pause = pause
        self.dialogue = dialogue

    @property
    def length(self):

        pause = self.pause if self.pause is not None else 0
        dialogue_length = self.dialogue.length if self.dialogue else 0

        return pause + dialogue_length

    def copy(self) -> Self:

        return type(self)(
            self.display.copy(),
            pause=self.pause,
            dialogue=self.dialogue
        )

    def run(self, *,
            text_func: StrFunc=IDENTITY,
            display_func: GameMapFunc=IDENTITY,
            speed: bool=DEFAULT_SPEED
            ) -> None:

        clear()
        stdout.write(str(display_func(self.display)))

        if self.pause is not None:
            sleep(self.pause / speed)
        if self.dialogue is not None:
            self.dialogue.run(text_func=text_func, speed=speed)

    def __reduce__(self):

        return (self.__class__, (self.display, self.pause, self.dialogue))

class CutsceneData:

    def __init__(self, data: list[Scene]) -> None:

        self.data = data

    @property
    def length(self):

        return sum(scene.length for scene in self.data)

    def __iter__(self) -> Iterator[Scene]:

        return iter(self.data)

    def as_save_str(self) -> str:

        encoded = compress(pickle.dumps(self.data))

        save_str = base64.a85encode(encoded, wrapcol=0)
        return save_str.decode("utf-8")

    @classmethod
    def from_save_str(cls, save_str: str) -> Self:

        decoded = decompress(base64.a85decode(save_str.encode("utf-8")))

        return cls(pickle.loads(decoded))

class Cutscene:

    START_PAUSE = 2.0
    END_PAUSE = 2.0

    def __init__(self, data: CutsceneData,
                 icon: str="O", username: str="Unknown"
                 ) -> None:

        self.data = data
        self.icon = icon
        self.username = username

    def display_func(self, display: GameMap) -> GameMap:

        d = display.copy()
        d.replace("%", self.icon)
        return d

    def text_func(self, text: str) -> str:

        return fill(text.replace("`", self.username), width=63)

    def run(self, speed: float=DEFAULT_SPEED, allow_skip: bool=False) -> None:

        clear()

        if allow_skip:

            skip = IOUtils.get_validation("Skip cutscene? [y/n] ")

            if skip == IOUtils.Response.YES:
                return

        sleep(Cutscene.START_PAUSE) # Cinematic pause

        for scene in self.data:
            scene.run(
                text_func=self.text_func,
                display_func=self.display_func,
                speed=speed
            )

        sleep(Cutscene.END_PAUSE)

class Slide(GameMap):
    pass

class TutorialAnimation:

    def __init__(self, slides: list[Slide], speed: float=0.5, repeat=1):

        self.slides = slides
        self.speed = speed
        self.repeat = repeat

    def __bool__(self):

        return len(self.slides) > 1

    @property
    def thumbnail(self):
        return self.slides[0]

    def _run(self, icon):

        start_end = {0, len(self.slides) - 1}
        for i in range(self.repeat):

            for i, slide in enumerate(self.slides):

                k = 0.3 if i in start_end else 0

                clear()
                stdout.write(str(slide.replaced("%", icon)))
                sleep(self.speed + k)

    def run(self, icon="O"):

        while True:
            clear()
            stdout.write(str(self.thumbnail.replaced("%", icon)))

            if self:
                s = \
                    "Press: [p] to play animation, [Enter] for next slide, [x] to exit.\n"
            else:
                s = \
                    "Animation not available. [Enter] for next slide, [x] to exit.\n"

            stdout.write(s)

            s = IOUtils.input("-> ", sanitize=True)

            match s:
                case "p" if self:
                    self._run(icon)
                case "":
                    return True
                case "x":
                    return False

    @classmethod
    def from_save_str(cls, save_str: str) -> LevelData:

        data = decompress(
            base64.a85decode(save_str.encode("utf-8")))
        return cls(*pickle.loads(data))

    def as_save_str(self):

        encoded = compress(pickle.dumps(
            (self.slides, self.speed, self.repeat)
        ))

        save_str = base64.a85encode(encoded, wrapcol=0)
        return fill(save_str.decode("utf-8"), 50)

class TutorialAnimationChain:

    def __init__(self, animations):

        self.animations = animations

    def __repr__(self):

        return f"TutorialAnimationChain({self.animations!r})"

    @classmethod
    def from_save_str(cls, save_str: str) -> LevelData:

        data = decompress(
            base64.a85decode(save_str.encode("utf-8")))
        return cls(pickle.loads(data))

    def as_save_str(self):

        encoded = compress(pickle.dumps(
            self.animations
        ))

        save_str = base64.a85encode(encoded, wrapcol=0)
        return fill(save_str.decode("utf-8"), 50)

    def run(self, icon: str="O"):

        for animation in self.animations:

            if not animation.run(icon):
                break

PLATFORMER_STR = ("Gb!;f>Ar:b'M_4+&e\\peZk#9l8^JqU6rD[&>@,a>.NqM_OZ%&V\n"
                  '<Y:encL.*[mBJe1Ca7?78AG>]VdeM-\n'
                  'i.7N9j\\Ki@i",<UQl3*fF_n8%hK9C)BJ9)Lq7\\lPba^I:qs<>:\n'
                  'Q`n`6ESt1G>f8P.r5"ZsT#Y)nbmj1XH^*4_GQ-\n'
                  '?(qG2dc*&hSiE*nH+f\\uhfV/:%2:TtK>%;*S%-*WCV)ns\\gOI-\n'
                  '6Y#kAg9fVi`Vm%=f*&DN[]5l3f,&q:a@"9ToGQd[eX"$qGtGdn\n'
                  'u/?%VA9p3,ksO7r!Yma`%IA8,/I/P<*SeoME\\Qp"ei(.pr"C%0\n'
                  '&2mU=^O6J-1TYDZV_GM:QD*0ud,*_G9"_krT-aC7Xb@Y<AeZP8\n'
                  '#$-\n'
                  ".JKVQ4K>?;W*V)2K:accL?'oZJi\\Y\\41]V?<3a$YD=kEe1SWRG\n"
                  'SOP;f-?aW6<)u%,tJ%RIB-\n'
                  '$MUB`XkR!bj3_2O/<.SMbMe7$e!.Y1/X-\n'
                  '"3YP&dPFQ/odi4@03BKJO-\n'
                  '^8JVf.L"@EAHEefaB^V0VBOLPO:/o_0jr7qao-Hl[>)Wi<)(aY\n'
                  'H$7.*m^ZH!8A%l`ctO@UFab=nLs#ZVZ:e0UW[7dJth"c7Gk[p7\n'
                  'Vf02KWE#+X%JP\'4![+HJr<e[&S:VKC.L23YDh;"6a)f;)Qqjd?\n'
                  'uoT+uq![E"M>no1H0PCkZ6hr6KMJrqp[_jK*>H=@=HYm8ZW!5#\n'
                  '.u!:8gNISiBT"5=*NS=siHE^j+O@da#64L0/-\n'
                  '#HDebmK0/P`pNmW)K8$\\fNl9gM[iljB#pn-\n'
                  'o$]FkLh9m5VdUu[93t67,Vqb[\\uF(Y)itS;^_7G2-Q:I8V-\n'
                  'hfDB"dgniN&\';VDi:Y[sWE-hrMQe3/FGM/3]S_JXOGj3:=.la3\n'
                  'EaljBMC_:[BMmdh!H3.CJfk$2`eiamaD@_+T%LH)@KtSTi,$3f\n'
                  '7/:;,?N]IaA`Ioi0>0I@hYfMgVCr9I@4pj9-\n'
                  'F(F.cUd#n>mFTIVaEeCAe#Y(8^4ipgoIHcS9l#\\lKQ<Zs=_TVS\n'
                  'c\'cm%7aW?W?XLp[g1Ms,taW-KrE;S.Q"<`3p>).(QCp<W49r!L\n'
                  '1J`SSrTHW*^V@8+L7ei1GHE`Sqh=5sn`pSo,U6>#g5Us=Pr)+T\n'
                  '3Gac2EQ`<DH/1c*lE<n:;P%O1oS&X/=D1T!9ebpCm+H,GB%oLb\n'
                  '^)S#"<a^^^r;lHgcMg1l3RL^fNWL`8Z5dD6/L\\,ciBcPhbrHjT\n'
                  'Is)PF75?J=d8A,peXi=S"LdRan;bVY188\\.7@)F\\SPBJ;+##ea\n'
                  'PJ2)nGLm<59O1K_f1Bf0uGr!n4lTCCGX?*rm1^,MW1d\\^2"bn\'\n'
                  'D[l;=[Hk)Hd<H8P5m<_N$iI@B2q<_N%:@PkEj<_;oFg5Y)Ke#?\n'
                  'A@o2[l?8ZL=hI(qeg37TKmY!uR(*6j:S[5;s1ORB&I9N*/Dl&@\n'
                  '8\\[5sbF=\\+;pW`;LZ<fnqt9/BaJ;l?%PL#?iL3W29N3PAp\\iXu\n'
                  "K=A=n0uW82'aBen_1M[QD=>*M)q4r+8Q;=*>gBKb[:I7PXj`,n\n"
                  'r^C(fme#ZtI-\n'
                  '%[mNI_Zk]PqkX3QGI1KkRP$`%DB\\D0AaJj_Kpe@sJp99`()E1u\n'
                  '"u\\N[MSQglaKPVNq7*]\\LB]gVc\\,_\'i(2qL=\'g_1G-\n'
                  'G(J=,h/p[L)#-\n'
                  'Mhn.#9ar_E"`jQu"hH&K"MYTV<aO.F:kqjpI#],@8_f?GD`W9b\n'
                  '@[jV<14.#LYklnr0Edmn%_.fa^uEoWZ+Z`:QE&>.m8IRRYqpW8\n'
                  'BZTOoB5%XbVB.kMTG9G]56hKo\'HMXH:I^[u8I"%;]X=jCYPW>/\n'
                  "[NdH]'ef*:W!rD+\\JT_Lm`KjPllN=$s,MG6\\mjI,pLD:Un39@5\n"
                  '/#a\\-`TV5$IMMAKpliOl7D@amM]OH*.FF@7KZWf"4?kd:')

EDITOR_STR = ('Gb!#a?]68LH09?*0pZn#"tR:CLUoXmh3lqV@JhKUepACW*CQ8N\n'
              'p>J*S0JGB52;?s=e%Kkth!>RX[]q@lCKlTaZ$D5fLP1<c)b!/O\n'
              'Yog1o":qqW//cV6-$FlOfaiQ$K-\n'
              '(`JhcJA.]4\\^UHM3B5le7ocmdJKjqs(6Nl`.,dgndf]qiOPHd1\n'
              "$TQ>Y8jC'^WL,Y-IH*#.9K-\n"
              '8*V%R*BY&Vrd=2h>]Q6F)&i)J\\6Rpto8_;p.JiGWnq_2BDg%/(\n'
              "Ak)h8c8'1nN#;(*ip2PncjUJC7&'(P6/aGOoZ)]_&P=TtSlmX#\n"
              'FiM@skD`4$1]60o_:\\F2XCISp5fTH1^Q5sb0G)+*2r"#53$l)N\n'
              '9eioXa#nD9f]cV]^p/=>Z+QLs!dua$;o:C[2,L$o:6>hS/+pU"\n'
              "lg'mY;sWmA#M?(pVN04BA?XA;X1tipRV<pFJVm#%qS'qK8W.<b\n"
              "P#j4Rbt3I\\aCMPl]F1JDjet'/NEiBEpPj?V7%dnri%CZ;eD(er\n"
              'R)Egj!`D(@6s_2=/_%8B$\\O2b&<.AJMXcEH^84RJQ=73ZY#L!E\n'
              'Lt7u%+&j4K1CfUNF7E!-\n'
              '?A%AS::$W9eSj.n2RGR#2qcJ<]Ih.1i7=[<]R_.dQappj;*VR=\n'
              'ca^/3Mqgn=%)p;GF;N"1_DcK!Q3V\\i1U].n+4E-\n'
              "a(ZufP+D2PgmR1\\G2p]Q*c\\UQ386!*UFi,FbZ[dDB[OG''-\n"
              "ue='YG^3MAsPgt+.h$=oeZGIrGMS*n?RK=T9g&:fum?A<g!h=k\n"
              '9CRq5k"*/QjFFK7H4rrW^4BkoWI#uL+FMk[Y6W7h%VYUdR_bD(\n'
              'Xq2?0a3bQMRHC+amP&.R5@mM%:VN.b@2ZZVM_earU[WQVI8tk)\n'
              "Jn]ZkL'I[BLX2m+0U\\d:S=A?p]UF,[6SZMKVQqJ7%cbEcSlas&\n"
              "W/Ih&a3T*2VQdUDq)>a.D:bi@(rhp0HiF)'6P;[9=;>9>kE^gS\n"
              'JB#e__jak"OZTTJJ<hAYK!dH".WY,OK1BP_r*b\\P5t5s=sKT;R\n'
              '@Mf%okIeK?<DUn^G(/j<GH5mVTR#eR8K!dZcP=_;p4kjJl[c>=\n'
              '+<r$9jUYMU*:gqV3koff9P"L"]_L,14iPaGujr@,rUJ?YE`qr\\\n'
              '#M*.?2njA(R6VG^B)ia**W@k:oe]:X+4B5mSU<s.X(bi[B?.5p\n'
              '#ra>^uH=2;`+o(LMU+8!$4T*Q8:LUrP?`BpR$#pK7SYQ^I?AOk\n'
              'E@KaGol4?Y^PYWX!TQ1$4o,^(-\n'
              "],C=H'iHWOXR^OBseuO<^Hge?E`Ybtq5-\n"
              '9CokLSNRe;PeaqZcR"q%n/c.67E>VoAO,)L\'5ZOIq/CN*;BNCk\n'
              ";KKsf19's4oG0Wi0'-\n"
              'a6`=%U5aBLU$Ah]_9Q";K]Wgk%rBaP)c%Mb@4cSeHW;#Ce,`Wm\n'
              'b+0++kPZLUoVn-\n'
              '[BTUuAmS$*G7So,01iY,no9;J5M,bZ.fFH%m`log!5[:m^9--\n'
              "'j66dp35sZo#9uBmpo6RAo:OW?7i`bVhBNN)G*X3hL[7)`@XS5\n"
              "?N&H3F@^W-G`/'9UR!$]!mp-I\\$:Ipl4VG12kMg<tL-Uo0(aM)\n"
              "'EQ?aR=OYiEi,1rKgX5;CAsN/)0Y5eZdcTS8mG<ilj.^kAWJDS\n"
              'S.ATpr7"@g]q10\'\'<^V9Zk/W1"RWgdu4;A+W<Ado<gY"NKpC;E\n'
              'Ll/PN^`0I2pT<X?;bftl/JAjRNhog3lg^r[4Gr7WZ[DgJMAQ^9\n'
              'aPm?(M8S3.1r@`4&DODO9Y7)d[tEBM`XRd>ej?b\\eGA("8m]E0\n'
              '>9Fh6c#S+8"37_(\\0#eRit_mK_M4=Fg8IfS,9JT#u=6^L9d!N/\n'
              ":3Vrb0-C<VdQokd1WM%:bXJD`O4?;Z:;0@7SBg0/\\A!'P3TP-\n"
              '!2%6$7)2I;INIUUV.Jiajk(5Hp5Pc0a"@U&KUn@oO!m?h8--:-\n'
              "4*gPETp*JK%pb!^PjFG[6MFRo\\e$rKp'ZCG(:sWi!]qjaT2^L3\n"
              'aV*e?G4Ou9!M(KZ7Hc^S;R/N^#i.:JcuJF5fe3Ih3UBA2.mBQ)\n'
              'OStZ+d!`573m"AAOSrX]PN,ml],Z!Fq4&XNc]pjFLL%tbL/+U$\n'
              'l2gX+TSaR_RuD4/Bb?\\G%PKW2*+;#clu9fKQd6sEV%u7OdU1cL\n'
              'eh@VXg\\<QM(&r+(c)Hq1I"a=L%*Kh9_ZpJ(FOZ\'qag&hF")m*Q\n'
              '<a<(/dM+%>1!i3k;3(1X$Hk84,=U>2"r/R,ZO(b[B7aqsB8[4I\n'
              '11Jc,l4>D>i#8)2ScjXC:*OrcTL8,o&&HpN]rpWKacMe4*-\n'
              "[%Nr&8`'J&g\\5fY!$bGP=K?3D.!!\\gf4Q;UL`jonlX[>t`-\n"
              'sZgOsVS;@X^`QO1B0!0b4(@adajcl`OR:Tt$qrKP-ePPeo.bmZ\n'
              "/l`@LY!^Xt4H'Ma-\n"
              '&_;Gjf/8[O"o(k=Yi^mEK5M%c<s0BU\\?^W8`Q]+TFg6AtRjM%2\n'
              '!.RoKCD$AKa/7\'U;,:M(h2ppD%p&C7o*:DtjdkqD;PAI"9<li"\n'
              '_tAt8C[kD)GWJpb)G$@4X5tDb0<f`.>\\Mf8>=7U5lGnEAge%1Z\n'
              "T*R2%]kMqFXHeL8k'1Wa7FcrD;-\n"
              '>bYVa,U8*4.aVkLT(QMEZBQTNPHU>kA!c#/4%h\\Q:ZcVO$CuUL\n'
              "geNMqPi'12C'D0PbU@fVC_H0d#R73c7.J(QV7IFNX+kE2CVoB/\n"
              'NMM:$,M/2G$bb%6h,8m>a(L5R3&?BtZ8K[BRgO??o@G74K&DpS\n'
              '-L#K?Y-(;-\n'
              "6X)%B2kf<N3$X]NMkF=>oIa8sW22c&4j09<KiUUAL7$+')8tA_\n"
              "sJGQ8RR7<0aUY)(-/Dp'RKnnBG--WTW?;2-\n"
              '9JRjiX%D+>?ON9n@\\//UTQOe]<sVq.`2b"en>*YD0!X%T-\n'
              'DC%M=\\f<jOW$L`Nr@h)FAsT)#:H/^"4KXOqe!n(O\\j[G$OpH\\i\n'
              '&@"F970.cDoVJnk*2Dg>pcCQ]Esc)a&X1X:h4pYcKh<(,"aG#A\n'
              'r5]?"cjaKc18:-\n'
              '"M=]PGR+Yr1Zq81gQ\'3XE!"_T5!?p1CZc,58T,>]Lc8kJ5%SIH\n'
              "i.pQT.kaZe3&($'[#b]p\\nT9/&g9aNumW6%nsF20&pZlkVU9l)\n"
              "Amf\\21RAc'd4d]F6FRW`qa(p06U$2YHjoP<01k^atDtbSea`3[\n"
              'B1"\'sEGf*Rof:>PO(;=m<#,C+J,*R5@Mb!,sP2i*$`1c4IWC,^\n'
              ';"30O>[GjGfoTn^`mbM86cJ8PBNiD6j=5g$#+!]\'H/U2d_nn;A\n'
              'Om\\BJT@7#)b!$T[5dV,NL+t5eV,up^itME8D,g9pNj8LQ++BFj\n'
              "=H;2`CD<o@MW:\\Ct27Zb$oG/'%hG3>fmLp,)5*CA3M5:(u&;ft\n"
              '.NiR%!e9?5`sTGI7*&Op82U*U(1rUd8gC+6pPqSaOKQV_^ii1r\n'
              "3do_o=MK9oprq@':G6AHTa#&?RJCdU9f-K-\n"
              "(646L\\3_)u\\?7KP\\GZqqsR=k:2u4_0J26+,9@k3'RK-\n"
              '8)a@_S0*OX0AucOVN,>=+TXJuV\'M"<A2IG]Xi_Q\\EY(F9^j./p\n'
              "/K('3LalPsC^<bd92r/]Pu#8P@rUH!\\PmJ(%Hm+tSpMEV'&$k`\n"
              'BX441jUeA2)#Y7GeF@J8Hl1-\n'
              "RE8CucF`;d2c>+2tML%eYA367U'l:V<0TQ':.ZQWGc'K5;n54#\n"
              '9\\3PZ1810np-cnE809D^1.FVO7CC=3#6hW_$,[m-\n'
              '7a1d2\\*=f"O`D2fW8+/$+b@OYB7aI6k0$5R-\n'
              'iTqJ`I[Et^6WfE/O]j?SO6u?%\\l<\\aU81qDK)&3I,:A\'SBgI">\n'
              '<],L-"9.R-Z$CLae9u&N.3-\n'
              "kL8='`?#^f8_JT0d5:8T09D.Vou$Mi4E1'kOC&j7=/UnEA`n?:\n"
              'KWTFN;AYOAWV"\'3QQ5$(^_2C\\8*o@qnSn./6_jWCnl_#A\'I1H,\n'
              '0CQdf"be"PSCg^!su.9Ck-(R0G[]A5j]Y/keB5TZ:WBW-\n'
              "S,n3_$eGMaj2.]M@1T'U=ge18%D3D0.kCNWY:L4'f+=(Xjag8&\n"
              'aA5F[mRhJi)=:VF7qEa6%;s58t1n`;AX,n0r=4q-\n'
              'QK60L?,\\q+@"Z=#q<i!bH[D!GK16r(N2o*3;P\'a)N&I.;egrW-\n'
              '5q@]EjPAE^P;/tT+P]$X[JnfN\'>d3[run\'+$I"q#19%E>pD"_T\n'
              "9%lo\\)p'u<-\n"
              'Lmai,)arb\\Qd]aUT$9(\'$OD^\\2$kED[kIBI\\/H"Y+@9NBeg<W%\n'
              ']))akcP(6iFlS$X\\s+ASr@e5m>@`Z+:)aMMr5if>/.gRae."Ho\n'
              'Qn$_<>Diu(u@4jh"#^NU\\%-\n'
              'E]/)\\MQ3MnhI+HUI:/^F7;n]f.q>oo$^mke.T"?<:\\jh,RKgF;\n'
              '=EI9&oAfbqE?t.^hPu]`7^8n,H\\2qg[Aira41nFNS>u1)sL6Ym\n'
              'etAq^h8\'K">d#L,Hr\'aso]D>9fS0-\n'
              'b(f_Hm!k":N1$55Cqe/f!ZR9ShWGME!kO*0`g+HGDD"_N_/V4M\n'
              ']M%DgG"BOD39BSJX2tE4aen%c\\Mr2PVXLIF\'WP)=dPbX+SnV[`\n'
              'diOQ]-P3?L9#%,JmkYsA$:gmG-\n'
              "3\\>2ncG3Vdp1FqkQFtSAR?\\*5Ug]!<&'#)B-\n"
              "C[/5>:('c^P<^4V<87=,hi\\SR$S7S?Sa]C[!Z)6W;8n\\hEp\\Aj\n"
              '/]m;p,%kNA6P4^CV51ZqM4cCOACqgSIW]!$1=3LbE4>RT^TFc)\n'
              'BC@)OI]a\\3R!1S$L"l0Bs36o0QbL(Ds^WkhULSqj*h!d3Y1<_N\n'
              'Nn+u\\3LUOAE&F\\mLJbpff6baX1LEEp`.U6KHSZX,QQWB>bH"kj\n'
              'aq;DXin"O\\!o[6l*T%#$ZCSP-rFDA%"+94pi^*n0U3:,k-\n'
              'm9e2f]%d0u,C5r(S$k6f_?G%6^HuFM9e",L\'e?FkN&O#Cp]LV<\n'
              "[E*IWX)cu%&'m/Ff/f(#KPh,?+\\_BE:,+GI&0lPtg><H1T6:N(\n"
              "=h4.7qTtpD4Y`+_'98Sb)@+[h:mbX$l*5$+q1.54PQ*:V:4[%k\n"
              's@HFgRa%KWnV<C\\UJ0>q;:jI;qmD:kQ]WoZW(E.f@rg`Ad`.F3\n'
              'K:/icccGnU1n;,(-\n'
              'Lj"FO9W%:m,:mWoeeYu1:N<@"$9P[ZYc.>$0HdZJNZ;6U^N-\n'
              'h92QqZ2I5[`8,`i=%*;cC)-\n'
              "Ec>)I'#&_&[A11XNnQ@3PE<c#6=m_7nIF542;-\n"
              'r"MfJtM/eP+fFBi7$_QI6)eGge&\'$VT6u.ur6gPWK;SGm/AS6k\n'
              'DENs\\F,Q:XBW6EjQ6dR]Fe&8N.?.o.\\CZC+^:)a<sZuQl.8iFh\n'
              '*Ya-\n'
              'H&ACrP+KYFb,cmE*m."qITW#cNSoqNes]brRUo/JY;?ulC=PM"\n'
              '[%/Cn^7FcaEmqGT0n"T_735<7Z=6NOs;]R@=AkEOD##(fb/ZOe\n'
              'PLXoQ9^Fg$M74PduC$j*`Gb91c_m2l8_+nH+?4,_>b,`q;6OT]\n'
              'kP[83\\GaONpV<V;MB4Nq54_em%L&gj_!,j6hoB+\\:_$a\\%0_?A\n'
              'JK&mVA6fE5X$AKupUNF*f7.)M\\mka2ks:ak#"LO@9\'4<:0mad\'\n'
              'cO^_#bNM/><C@>qmkGWp7u\\GpZqqr<!Zg/*6SS:59E")M^7(ZT\n'
              'Nr"gR)&cWeJDg,qZ0gFu$(?/pll6imUq"H1-G;1-\n'
              "D7N\\oTPHf<m&4nQF!.Ek]O:0g[jD6\\'@`U!_^H:Pm#eTJ7(GkR\n"
              'U)X"L0sVHYJCXa%M_ARYKh&hdKe@hV&ZCcZK=<)KRL[[^%^.hC\n'
              'S>-\n'
              'PI4&`@a0i^@GZV8XcL*ed^mq;ghu3@6C<Z$r^Ot.KNDP,nYt]c\n'
              'K-iU:8S%bH0\\#+9P1k,Un]c]Ho,aeZ)kSnH`!ULR85$[Li4S@o\n'
              "BGK0S@2/Y;ib_X(MSHdhO'X0*if\\QQ#7tX1R$2Yn!A)4WrshRX\n"
              'uS?Y!i6U&`+FE15WtS=8h#kFEm:W;&1GXPO%LfKNWTnB5G(AIE\n'
              'g*GXU%p@bMC>6ONDPqsP:IFE;(7XP(Ge=uDFCAC26A3>#*eboD\n'
              'ZpKJ\\XSO>r^Rl<l(.AhL??Zo-jp1tTIdi4@@i\'kJh2QF%oXn"D\n'
              'rhfj1k2<SEi>WlapL4CjsW\'b66oD,=b<rr?DA*"oB.SO7g^`@X\n'
              'Ko6L/FmWj,*u;b%=I2dZIBM4E_1DQP,J>+=Xm3rI-\n'
              '50T\\5YdD$uo!=.aHnWp)a=N6(7?')

INTRO_STR = ('Gau`R9lJKG&>`*)8d_Ms"Gkg*&>_h7!cas$.Vc!s-\n'
             '+";AKFfWu`gL@3r=O>,KH-\n'
             '*3:q6;?Ee&YZ:Z,S6]5_"5"@tj``j0(Bm^tJ7DnMS6fe8,=Q]1\n'
             "=4PrQs7a&DM5bsif*B,,&Bee'CG]YcjZauVAdqE_enEJDJup=O\n"
             'o1S!F$PSDoJ*CFl:ZBV[a.W3HnAIC-VpnIS0$P=?sZn2ZJt+Ok\n'
             "'a5AZ#BbLg@&p_$q#dFd.Ir`.]34qfSc3QqrdOk+XI83KnDkiN\n"
             'aHDq*iL8BHDmFC""[piX`T7R7Ms1I3?KNhK"0-\n'
             'R4D?!2^pCbjo>F5dotM48Qt?K7/!iR4J],oE0^<2F(8S5>kHNC\n'
             "?#$:0j]*EdK*$3ro;nXLK,6sR2N`O_XGK'[3AC/ca,/1Wi1U`L\n"
             'fP]+/L]ie`DXC`]j!/YmB/gI,?,Yt%7(@o[EWafI^QPp"e5n_6\n'
             'kTR4)>Mj<-\n'
             "JBX&H;R])'!/+LdJtjH'G<GDMSKH75`!YHe.P;**KA8`!B(V>7\n"
             'Hce8$OtTQ3>\'q&$5%q,_9OF4YPYO)Zr(SB"D1@mKF!NSfgT9A^\n'
             'r87r68+/1Mhp86*Nro5F?hHuor!cge:TB.CZ#Ki``^q^+k*6J%\n'
             '-`ZN\'QZ\\CG2TrF96g5^*Z\\V7BL%:"#[Q"SHQO*nD4Pc5-\n'
             '6d2%T%Ki\\-&8-\n'
             ':,dUc%#ep[$Uk?I74l>WE0Hig#V1<T=g9?=4Es>PbCo40Q*uEb\n'
             '/9?o)Q!d&--fEm-\n'
             'V\\<22QJPO2"q#g\\X8_+.pVu&*qqaP#:m_#Z3YP3C[01qe7$mVQ\n'
             "S<L$7@h^cC;m'/J91#TF3Ct^#s,jLjoZZ7?aN7plBWVtrtFHO+\n"
             "5BO0KAYrN0i!U*O9P'VdoL_^VtH\\Ua/?:4P`<l3h[O+@l2S@&2\n"
             'GmBjtQ8P=pA,C)>5"?O0KT\'QFn]^;Nh]Y_3q\\E!Oe(ie]1&<@M\n'
             '&q4&5\\"[Bl$$GLK!7pS5SjU2$OS9"Z$As,`jU@f2qmdgD')

ENDING_STR = ('Gaua?cYjak\'ZZ[i.7Hsb3"QgXd$QX8Pfd`i;bP1G8/sQ_;C/Ii\n'
              'Lb*[XO$/ub40/;lgBSu`P[8`I3P[jWnIJT<7MS8L=Rcn9HKMoo\n'
              '=aScomb0t&)eg=>pO1qGT/Sk\'B"sc/iQntdaJ7tE[jS,We_Tr[\n'
              'IYm=5rSDBee>ZlemFQBccF0\\Q5CN=/qmG0"LYlCEaNj^m_rXrb\n'
              'UIjI*9^L<lN/J&-\n'
              "\\0DZ6'bpFCpm^8A.[Ja9B:or]Bu>j_?bns=*Go*;H0jt0I%4Q,\n"
              'bkUM>94"0PhLbb#UO8*]DiBab07T\\CR]&8L4SUsW:\\3k=5($HX\n'
              '2[l_@2op`NdorkrPN3%JVi9,>R1[[j[NIJ@n6r-\n'
              "KXblL#p1s%!1qZbf_'Ni[L+lE=b]%BmksVi`4VEd^1h_f'8d/n\n"
              '>>N<m";m\\,qB!OFTkecJN?7#@]mNUDmFi=1h5bKV)!-\n'
              "Hf!M((jKQ[8!^P33EbP!M?'J=4U[nKT)>NE/FH#e<,`[isAdla\n"
              'GjMr7susYJr/+)`:^pcYd=FYK#rPfB;5\'fC_/8%D"`9\\%_00i7\n'
              '<)m>%u"PoK:@dQZ7K3FElBm\\u;M(7JuD#CA(BM^]ai\'F3[B*fb\n'
              '?I)/Q/>>S.1[2Q/O#f3)qf,<6!C#I.tI+J_XH_OR71rqk0$CV7\n'
              'MT4-\n'
              '[8"McoSFJVf^?i9+K=6cj?JEc1,hG=H6eqMj89Z.197+)W9hBd\n'
              '[<,.?_]2b0!-\n'
              ']V(<Mo[;1ZQC<,]m$.]pRnLKo1N,uBlaQK0bg<VXI^frn^:4h1\n'
              '*H,_q1L7U![N!XZ0Q:)U1m=4:Wd$DnQRF$5ag*g3NZabUqAMXY\n'
              '-XbO[g\\p;Q.D>Hl-\n'
              '5ARYZjX\\A;:S$&`[<c5)lGrO8n\\J?Voo:bu-eN[f^7+X-\n'
              "?cQ!l3.@UaL(=4&RVSc;<]l>#l1t0;sHT;9#r[=$*N\\D:Y$'ph\n"
              'T\')LE#0MYh9@o@GQ(5sgSqAhDWUD>\'5e1dO=/n_d[G=#OA*.":\n'
              '_(GuJ%Fue1n62]5_!ECHU#bHSo6ii9J)FA8uDs4UOKk4KQmb#`\n'
              'l=MWp(o1gG:G@I%BG:X&R6f7$jTRF.dKT[<;7?A^:@%uXlC2-\n'
              "adX'ss;DMRN4gQ/bTdB=US1s+Kkd1Daaf9g-\n"
              'kT$2$0#I@#:a=?#U\\pKouR%?L=Tl8(JJZ!IsE2ts-\n'
              '6]WPpKpZ.3ba-\n'
              '&&JcErdn0^ik9M;,.n]1S<T8%*nkrmW41#m6!B%;ujPXmV8C)#\n'
              "'m^WfYED\\o117.FrB9gBj+C8=1/X7m!Ob+C$B'%u#]Fi$O2kT/\n"
              'QV!RHTK+0SR:=Rpaee"^<2MJaR!B%P,Er,FHKdm-IKN_KNFa9i\n'
              'qM^[l+9=]-l)44fQh)"S.Ggg"K#-G(4-\n'
              'F+%ttm,`;X"gYI]+IDAU(_7%WT5cYtiA4dj7R?;eU_K&QgDe\'"\n'
              '$6;$Sn`Tgq;D.3-+6$Ut0]VmpX,:0"qYQFQ&bee]M2Ng5GdSC\n'
              '--kf$>g%6I06(rqn+9$l,8BN5ARnh$Ne@#RM5B"-\n'
              'CMb>QPQ\'c"\'[Ye%_c%^cX_>OfdarpN\'SiY0mPJ#LC&STomX<KQ\n'
              "tb[T_6lk?I_VZ%tJRCMSc`EXjH'I$-\n"
              '];G]7RME.bi+2dUf@i$a;?hI2d8VO0*:p:3"Fh&5i^NVnrD=YE\n'
              '>1[#M6^[_gMrd0saWB[gb>Z>!0LWdZ.$dCk9]aDno0^YPJr"tI\n'
              'O6dY;uVkg-"[%da+cVVQW-K[a91B9&E5r\\2KV-\n'
              '\\,3bVN*V/"9(KaU3J*a)f=<eitH,V81%Up\'fEZ69CI&&ET\\<:p\n'
              'WmoHhO>T)]cpl([p>`]JG^H-\n'
              'AmbfM8PgUi5]fLMI`(P;c6ML2dS35npB)?,I+SEnoq!E7gf5OZ\n'
              "+^=PPefoN'U4T(r&M%gT+^1Q9o>uEAPt^o/H%5+]Mk7")

INTRO_DATA, ENDING_DATA = (
    CutsceneData.from_save_str(INTRO_STR),
    CutsceneData.from_save_str(ENDING_STR)
)

PLATFORMER_TUTORIAL = TutorialAnimationChain.from_save_str(PLATFORMER_STR)
EDITOR_TUTORIAL = TutorialAnimationChain.from_save_str(EDITOR_STR)
