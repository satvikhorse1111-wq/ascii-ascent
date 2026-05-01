from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import (Iterator, Literal, Iterable, Generator, Optional, Any,
                    TypeVar, ClassVar)
from abc import ABC, abstractmethod
from math import isnan
from textwrap import wrap, shorten
from itertools import product
from copy import deepcopy
import base64
import pickle
from hashlib import sha256
import difflib
from zlib import compress, decompress
from datetime import datetime

"""[maps.py] Defines all of the levels as strings,
and also creates a dictionary that can be used to access
the map string as well as other metadata."""

type Result = TypeVar("Result")

# --- BUILTINS ---
GLOBAL_STRS = {
    1: 'GatUn9l&KK&;F+mE"C4Hf-r`$L18@&nA`#k&/pb0L-\n'
       'XLWnR8ge)l]+067XGY:h]9DlfKk]GBPo:dno]^OB8)Dn%A8Y+Q\n'
       'cnkqIXs7<didQBVg[U/nff/>++hkE+Qa%]k`&&2LR`@kK0N*pH\n'
       "4kMJ$0XN08)Q$+#s9Jm'lUK@J3C3:M]rsnA/SgNK<'WG2.[2f+\n"
       'S)1p_9-<0AT!\\kkL?.=OHeT`RiI-.-(O5XlZG@6WdaV][^g-\n'
       '6IrSG,@mX46Z`*%GMhEajtJ^XNp\\LH(:S49aB41.F(.L0Fflcd\n'
       'WDg;[[nFCZRHMXB3(741/"uFV]tnKZ_m:8H!q4P>>&s,B4muk&\n'
       '/g`ECHV+"F.4R:%-\n'
       '*=`F+q*X?(DBr>W>&H,CW[Qs/c"$<\\13\\2Q",HUZ/!Uk3o;qq6\n'
       'J31-\n'
       'fQ.Fc]0@glIuQ_J,7ME@s*"6*^\\VX2,?eptH_&PI59,[#;;_\\C\n'
       '2rIIA_r*5)i,!-"S;$qFknk9_,UO+m&h]n5pLD%\'fM<-\n'
       "2KLB?C=mR5dBu1BIA-)4u(^4ml#]:P:quPHDj5'",
    2: 'GatUnbtl2A&B-@hn3FjQMh`UlTJ<aZ=Fgi*7ZG52-\n'
       '?:DE=CuD[BcFW#3LK$\\m*5)#[9t\\E?\\%V;Ap3$Lp+VPqfB76jV\n'
       'R"JU+c8kSc<uG<7.`gX:\\6n`SPC6)Q^AQcT?,9ZbP3hfCD%%cF\n'
       '+Q+SDaZ:<L"OVX=!l/CIU]DNLO!DZpcW7b\\GB>$K,-\n'
       'hP98$Z)IuE*6><naM>l,@7-\n'
       "a0lNn#eP9lQ'X).kgIU7A/G'WK8R=7HWS89@VYG\\I6&;T:+c;F\n"
       'O@p531?@.km7k&FWSWNM/VDL)(4T1Xa6f;\\l/kg+!G*eA.h#d1\n'
       "'e(XKYEL61$)m(]q@b)pH)S?hb>$0&5E!T!n'MT<N9*=jJKW:\\\n"
       'D=O9VHIDq%dCD2o`hU&[V=cP9<^CrRc%dXJE1i89H"2b*ln?hX\n'
       'J+2&7tT=rYC\\?Z.A\\.U#B)4O_:&',
    3: 'Gat=g9l&KK&;F-KO@q"4"aV)^_`H-\n'
       "kd`Sj?>oY80$*GGu?Ahpf7NYU\\)JN4'LI-\n"
       "@F>IXXAP$Gu2@oCeMYfs/9I:fi?5C1(9n#4c%p#^'fC3B*=c#L\n"
       '`=qNnqkWP@bMH<qukk;o!GNf;$(fTY\\(I2LpoC4#Oo"Rt^*lho\n'
       '==qZtqk5P\\M"2a-$b-+"DNFiUYiDsZPS5(;6p5JcfWY6blP-\n'
       "Q'iueR=,j4-\n"
       'TaEjp`@DmZ"\\Mp^$8oS"bZkBfr5\\n7;OUd`GX4L?a$FB:/#LWB\n'
       '1$eN[@c!?JahM&7NQ,4GJfK+VkW"Jq#6HHMTt!I))qQJZY+\\F[\n'
       '!^R-rt8].-\n'
       '2o?nhuQIXGk>?$0pVc>dFR"T+V:d&Qjp\\84]aI_Fdd6Er]i5_u\n'
       'aIILal.BQ$oc@h\\B7Z5SsN!!!rtQA]bU\\J<6$&A/NE8;l"E]e<\n'
       "@Z?9@B'o/=d#B/SZVU5;=9E\\`df[KBY17g<B/C/QMm&Qr`CII:\n"
       '_)5e>/j@@#d@=H?9F:1TbOG$s[m@7NJgq.$%VN"T`\\k[)7\\tq`\n'
       ';)8G&;8d\\dfgAOZODcnX,b4GA*G2USY^&"-7HgC]',
    4: 'GasbW9hWAh&;Co%]gr;[]rp^uK!b>KRnG9++uLLmCFP`p@Y75k\n'
       "R]?!&k^@B0s4>brBhI,:mpXn?R=44gL&DX5c\\/'Ce[Z6q0LB*V\n"
       "B)u*c`#lYi`_YYCE?#3ck8b2Y>V;8&CnHS+(+'/Vf8)Q*,i(>(\n"
       "V_US:7HnbNgutsNRMuC@9qY';ai&iqV$B/Z2i7p@d1)u[+gmfc\n"
       'Xkk:lL#tA*4s]g*C.MF:lkQgA"U)DpYVepb&)1S1&an3Q\\slMc\n'
       '0qhB(q`L)gPc?5V5\\0KO248a;l[h+1(YB2`<I*[<hSCQhNfSG0\n'
       "Jm^WDgq'ZOGVGOM9\\cT^]gUNq'8#=[JGd(K0H\\A?8EOD)+3aI4\n"
       'O@=?]R%HR_JK#@WCc5eECSK7APbp"Sq@sTb;isdW,u5<IXtpu1\n'
       '$@jY-,?7h,(-&bZG*rF!()T`pg:HF(P+dNJ1g*d("!l.=-\n'
       '&ie:U)9&GF):aTBs,d@',
    5: "Gat%_cV)/0'ZUpn?G(ORqP<$`7(`*3g0>=[7<B[9<CY]>3jn9e\n"
       '11^\\Vn%&8lJ\'CH)D--Z*/T"kc?9[6nBjP!ca/u2+[T+hf,CsV&\n'
       'P\\%MJ7ei!*Dtnp!7JGgODQ<l<b0j?[#F2*qXm[I(&Pdd!=LGZ)\n'
       'eca0phsWoI^Sk;o!oYXd"A3CYo<:\'7dRs?P6J79G;2e1I&$`@Q\n'
       'P4K<b&Z3*BpXHR<!-MHE+@(@H-,N!KR8>Z-n%>&-\n'
       '/QGq<&E\\o$Qmc2&fFY2Z`SrgU#S$AUs%s4@Ij/hDWNF?q$N]Xh\n'
       '%5J//93+S#UbKp2E6BO53K>1>nU+WE?LT?A#ThhSWJqtFnmZX0\n'
       'VLs-\n'
       '/L[o8Kjum]7^<^+9S$m32fuAQMJIN9+$iQA6ml1T$>X8jsNu[T\n'
       '.fa*c=H+8])7-Da.m95hrZ-ah+"[f\\+48U%2T@h*>"l#pbTu;Z\n'
       '.*i_TqVLBM2Bor+hlZd:]LEm/C^lH$[YU$U33"!=&\'8/Z<a/!5\n'
       'B6.kE7a0UE>NSFX_mX5/0Zej(',
    6: "Gat%_cVN:L'Z\\U%e-gK'&*8lc+dtHR-FjgID:;H6+gL>ifuYbd\n"
       "RU:s$FZiFPm_6sC)u)?`dN>uqU@=F!5<mnppO,p:VtL(`FjR'3\n"
       '=p`Ha\'^a4\'_%FrR5C**,rg"Sp^=n\\+WaGgRA8En7$#M-\n'
       'e#(j+NB_2WuUVTFu2\\PCKR\\gW3M+XB&^"C:[e\'A<E]Z3B\\@J.m\n'
       "6R]E]OTVAe6?GKM%SHQ@ND8MQa5[.,KQ#O3TCEm/O>:6i/cN'R\n"
       'QKQWb;&_$p:7T(P2g.>+!pCgjdM;iLR4iUG2O2U"\\75UAe@GI-\n'
       '8k>?O9=ULC[=@@PR+e]R&1;j<ILsnIV>+EcE>I8><-\n'
       'cTQ;n3@tS0Zf4Ja72.[,>?96kr9XPHbOfjeRP^_oqO?]$fi:LW\n'
       'd",$#9%5T_-\'`lTQ;-r%":m6*.i!mSk(TK?JF]-\n'
       "L40K:5_u2X:mr+*NIf':5N-\n"
       "7jVIf.7ro=Z'+f<'@Q8#6u3g%M:n=;Q8)BsR%q4,ia8o\\ZNh4E\n"
       '.C-\n'
       "F(n4Zos=lj8s3h;Htr&l'dW$=T?5pWS+3![Y`i7*TC,;G+!8)P\n"
       'PBR5S=\\1;d\'5.A/d#\\iY1"Vu,>3=]#hEejh>',
    7: "GatUocYLBO'ZXc`]EfRlG4ad)bV\\S<g5Ei#`c-\n"
       'XJFqmTtFNXMMlXV%@gHE$ZrP*F-\n'
       'g,?A^ljJC=P*aMl&b9*(WL$7^2+;d_(EnV"*M%5+0&R\\o^Yf3_\n'
       "icK5AK8n8YMIi]%2-PjG'-\n"
       "'`NO!_6.Q&Ze)f!&5Acmu&'G`XpGbS&n@\\H\\I(9X%I)EsScq41\n"
       '@X9`:gW:BlBUeG7Nknm-M%r>"KN7_GcUrlD06?:U)-\n'
       "4Q)7n=SsUuX9hW'R#uX/D+\\*.'*s+&Elf!NCTO/@tpRTi_F%+o\n"
       'Q#@*t]OpC%:2*?M?>uVp@MGFp"7O?H$piIRYDg[&Y`dG5-\n'
       'TD<OUHjSi*\\+u/9h>fmOIj/XR,Hb;#`S.-\n'
       'h"joT2XcYM2fXOb>@2!He?$UNWoIT.!NlNUB1%>Zg&mm"%5oS=\n'
       ']%Uu<<0glFfRMNXnFbZ#oH-A$)^1SYP;oW5PQbO0maFs',
    8: 'Gatn"cV)/0\'ZWY#]6G$5NT;jQ\\1[%"[20\'\'LM0!#lPO@5lA"^3\n'
       'b8BRgkWLlbs6KN&9t,E=HO,$aqKX_Iaf"iRWZ<C##]7H@>`)^W\n'
       '9u(7[q(487jG+Es)o!B6L:BMq\\ab:C"d_UOJ>>NI=MZ7`2if+N\n'
       'DP!d>df0YJntB+j6_#Fc]*,5-\n'
       'SQKd+W1FV/Q[YT_lD>%)@bm:TEIJMM9>"]iclPM3algkr`E\\+Y\n'
       '0K2>Q,:O01!G=40r7)BYWiFf*T-\n'
       'iEh;F5g>.01sLpYH/:,.V8W&ZKr:orref8d+m\\#_,DIpVhDr"]\n'
       'I7G/H@N>KZ0=nnI+%=lKR=A[7=?846jo7Of3W28R2"aBH2t>]"\n'
       'FY)1QT<Aik]>mfG[<K59,TfQP#lp2IH>t_5+"K[+V0J@M%i4)4\n'
       "!pP92,!=8^TC)MaChKTbH'%Fc;>pfVV4g!44fg,Ak1agEA;'a:\n"
       "H)m/K3?-&g3n.J8%#30'2aZZF%T=",
    9: 'Gau0?9hWAh&1uU6OP]XiZ3VAEVYP*^Xb_kaJtV&$PYH>M(>>Q0\n'
       '>I=]%msB-\n'
       'S^W,o`FAq_j5aXL:1G<ZYfsgP8H+B0m0eZ>l1_IBHN@2)kVrC(\n'
       '6]Sfj2b]hM<d7Zb51.)ESDEc_BBUr8%1D;MGOokkqZXScoA-\n'
       'R5s_^`-\n'
       'U;6a_#K@K\\FMH2_8>$Il6QZ^IN>VbA6@R0MDZB5i_g2bVP%E/u\n'
       '^b2qV>e,Nng9!/7>jl[i>9)G#lDpqMo;]&;5::>h5`3?eG741E\n'
       "U99P1@C\\UWI5;>u@RJ4`Y'V-\n"
       '/G]IZlpk4+\'obkrVP1Bp,Z"/2(^%7tRg3d\\Mc9:tDbRUTCYqcu\n'
       '7>iq[-\n'
       'sN;O7sfhE;Oh.2VKSm_CO^S@CY7sAqUCc$9C*mJ(J)@RKGj,a;\n'
       '"+JoI_0rrpl![h;eLY!T%\'JAlsmbnuj^9?g7%K/t!2<trUbLJI\n'
       'O1Z5DdGe;Wc4[L/rUUk"r?@^Q12&_oT/_dNn*#K,og;Hd\\Brd9\n'
       '_(qN.0_m!.5&8Z,V_*n50NIBI-',
    10: 'GatU/8T3\'C\'WrPn*.$Vml]^Im1.%!WM6lu?81YK*OXe2$"0s8A\n'
        'k9_Bm/:1RA!=?\\eD@HQ3=_bon!Z/R!So<KV]g\\CYXku?I-\n'
        'Oprm[GcD1eWWY?_&:Sl0E(g(rh_?uA)kq.%%4a5R(s;ql?oos*\n'
        "J%6)64'@8paJ)Ego,oe@g`n_E\\BoqE`g=1m)rNurIn3`c'],E_\n"
        '%s(toEnU&cQcuH8:;DOd%&C0\'A%k<R(0fO6hYTQ[a7ii8FH4K"\n'
        '0GMeG=1Xnc"2,\'7q;.kbn#92<h[&a;XK&3X&JM=M\'[>/["=Wa]\n'
        'iJi%4MZN"CVGD.,kQ\'N@gZ/4cq*%E3);^%D`p5LY7^YML&ZcpF\n'
        "h15sR-CY-Fo'XpamE=rHaV,P&oLNt/9mb]#k[5Cq=gbX^;E$;6\n"
        "T<N<'6QLVc*l9<:=Ia&Kpd=XV;#-u;c\\t+4AL70O-\n"
        '"cl@Y)>^+&`"<@[3h1P"Ea*>aDVKhSOkW+SfXQ)]NJ@q.P^9Y1\n'
        'Ko#j;-\n'
        'eh>t[Hp^ib3>$14Gr`aQC<Ka]f(o;bCHbg_624Q"D/_6l<7H_#\n'
        '&X_a68+!T>0hZ\'b4CHD]6"hiD`,N!YV99Q\\sl0DH(piHQ1L).t\n'
        "/YG=<b]h'#-?)MOrs#tt*(2\\mVR/Y\\i&3qreJM>!h",
    11: 'Gb!$BcV"=*\'ZYij$G:_61\'d\\"29u3*k+YZf@Y/">LtVH<MX.FT\n'
        'CTN;amW31?Ip5u[XUL.@IGlo!k08;1&"&^-\n'
        '4(`XK*QlT&Muk="DT!)j@\\hl1dAqRoLN5<`W;G5H_R>>"O2k9\'\n'
        'P5+<dKEjgLkBq.RiVL$:<?]b[5W03FWq>M"Z$n(i\'k)5L9(`Y-\n'
        '+O!0"nR=r>E;t"YGu[^F+qXaAYiS!q49WCD@BF<9JkQ!\'O=6Ye\n'
        '-RLA`O&rW!5A8_D9H\\i6^EB2n:*3a5<&5o.dG1ct/9u9f6RYDm\n'
        'Y[$\',"<b\\i_5KT6f_)g`$P*Gif7g1g.B)B[gqUfUFJ2r?]cEMZ\n'
        "iQrZBl]0H'qri_Ccgb5UA$GlsnTUPkmZfUeV!56*c$H8f=2%`E\n"
        "+nR.*&&K@t9AklIo`H`n&Qm:`R@?@R'VhWR`^7d0e]u=k)5GD,\n"
        '!B%F-\n'
        "37FSW;R1I@Fo/gl@5,`t's(5HC0e/TlP=![A/9;91;i;_b=81L\n"
        '2-mNtl=eIscHn:fdo)l#r;am*qsa',
    12: "Gb!#W6#35\\'J:Y>HRQ81?Di$^Q]d;kBVLgrQF<#W.-\n"
        't9,o$lhLCndYIUPFQs5.=;eDo\\5b\'/s_<^$Gu"^NjbmhD_4uWV\n'
        'u\\"IB^^OD_E8/"oiZH96;9l0B1tor"eJ.,n&_E,\\,8Q-\n'
        'H!!b>t;&sC5IgK3O)q"ZYbai/tr(5IK`_)?_=g%dGl;inr:c(&\n'
        'XBi5"6IAUUG,`kj8&m9rZ\'&:auo#=e9@^%Xe9NXaL/-\n'
        'cC+(p<?!a&d<g$&A_>[(nF]"bt3N;5&LYYY#n5]DjCQk6RC]5q\n'
        'Y"mogp0,0LlMMD@i@X>sSH,[da/jFNR"Gr2t\'+Fj39MA7Wi>qp\n'
        '7"jra**Ulu4QVgXc"i8u`A!l),60+h+;Dic@,g01JH=m^%/s7b\n'
        '782`gJa[\\Zu:_60la3a9u]7RBT,[(g`^rpb^ljY_U<CHb1&BK!\n'
        ']OZ5t^\\[t*>6T1-\n'
        'o0Qj9FIe6?LIY#"J+T]DTBtpS?H]0`OP#0Wq1Reip]d*<j5gM^\n'
        'XR3&a;(n!``/Z,:U)8eXiDLptJ3b%<B5#<%X"Dc(PI5IV@n-\n'
        't7BObrKFW\\Xdr',
    13: 'Gasal9hWAX(`(oRK-s+#7WQm#Y"N#\'HVk=hR0-\n'
        'l(V6jOnL2N#oC3C0\\St#9MRPmn:YmEV@pAKC8]Pkl(j(G9pQJm\n'
        '?Q`kaJDI,d7)dp=^Chr=,uI#%m=/ed51)J>]IV@Ap,XSe3`7d>\n'
        "5q8Go*RgrNlkiCZ1tAP-Bb_,C\\=O0)m4;C5:sQa<Ul.p'ec:N[\n"
        '!ZdU_X@Z6o`:cP<]o)%qD@TIO&4825Cp6"?6-\n'
        'qJ$?X=#j;on5JBMH(Y5l\\)JsGL2?]c^X!TG>epDj@=Z/[]>g-\n'
        "kR$(?uV&B,pFA7CU/,qgb'c7D!DO-\n"
        '?j:^38P=>7ffoAe3T!q;7q$%ha1_LJErdG<eVVQ@,UODjlkUF2\n'
        'K1qF5+UpE?*TIF6m4S$t0B%,+elfD&[5NaHCVb;^P3,<D7M9]D\n'
        'CFnsJXq-\n'
        'Z<S]4btBMY4Jdm+U&[uF:e_`5k$oU\\(\\?GCda;69g"@sF9:lVJ\n'
        "tLf9`l)^=gMu!L-H)U160&Z9D*m8*E^CS+'0GV)LNZp]U&f99-\n"
        'g\\e1Ba7))R#8F6rWU1Vkgo',
    14: "GatUocYq8d'ZVT'!tLOI!GMckDt9Uh5[3Pbc&YMP&<&'?KEP?j\n"
        '3Jk(C:#i0D7sdLQ]5O):(WT:^Ca^[F;OkBAq7QH<q.K0BbMIfu\n'
        'JG3(i0*HcR6WS:uEq*?BIu,7V^^k!AI$5Wn!;N4@lK>..<c)Yg\n'
        "Bj5O0BE^I'0#2Y&+:SU.3oVSTX&]Je&RcbLWjX1[d[LBC[a//V\n"
        '"K9^sM?)li>.(6`4m6uN6fY:R+)=2Y+5H_Ke3AFVBQm^l:ebnO\n'
        'kG[gY8R"CNO92utI/n:f$W9(=oUu513^J*7\\l99U4A8V7\\,QfG\n'
        ';B8DQ(B5a:5FJ-\n'
        '?I^BJ\\RL0"]+)U\\;[gDlrgT4YdGS;[74\'9p:!@3RHA^ReC\'E0N\n'
        "]@S6*'$=d#Y&,>CJY1S'p+\\<HsJnF+]QEXM3=#AMo?B<7/Y/.G\n"
        '?1elYWi,@IP=<QjP,2k)NR4P$=!)$]gb%P+HN^uHI[WTJqPH,`\n'
        'KQDQJgTq#%M)"de+&5&f:b,ZY;rj4mP\'=8&D6[nr5]&/^!(QpW\n'
        'fr,cISNf?[o_NVG_R^`QFYmI%8Jm[7h%#r2I65!"%e$1Koi$<;\n'
        '/qoU(jK9N>QRhK7>_m6LX)@j2bR6(o!e1r8l^nMMZIf[t5pkA',
    15: 'Gat%_6#W5X&;;@J;1",KhJsWP0.r*;!J:iJ7&nrhE\\\'XOH`YSG\n'
        '#91Vd$ZNHm.^f#aFn:(j(s$1`coqbZB4q#%NR7[i]jCD-\n'
        ".LgW@9fK'0n*]BXB65BtLeke):GLe*77-\n"
        'o#2E+Is!GXdL/"*u3WY7?=YtlL</gRUlKhT!>+FF@4=@H\'I9M6\n'
        "N$_oRkf`,>da;[6Q\\*=iUZ+g<1iF:)4_9'r]BF)-\n"
        "BV*Ni%sSTI!\\#`Mas]UA1#p:[R$4Fug?@cr9gG#T0PNJWm9%'n\n"
        'oH-QqLmOXI/89G6SLPmCnrd]!0iZ2Ajf./WrR"8Q*fXtUL;F+2\n'
        ',P]:5qC5C?6=np$XSQd@Ea`O*tK5MupP5VpCMKO;rB*@LZL+:.\n'
        'oWU[1/Oi`Wi`S#]ImWA5s,cK/=?1n);`1WYjfc^;Un"*%:/5)-\n'
        '*l>!NWGC"=)JE"=ClWiBWWTF!rNjCLUm[feo*UV=OnS"B3BDoK\n'
        "P*]#d+(:r+f>`jKD`lU0L>Jt_9C\\tb>EE@1I_0h4h`'0i]jrb-\n"
        '3&-\n'
        'I0Z?0ql=bH`!J?k\'1Fk6(m1=Vj=;rhGDfde"9aNNZNLGA4$5&Z\n'
        'f^aX',
    16: 'Gasal?#/1K\'J1kIHg#h0gF[$=%@_.VG*;!aKm"C]%1K\\s@H@3p\n'
        '2Kc*/]8[7O[-\n'
        'r=1p4"GOEVtscj+\'=rFRD.j&pj!EHL1$a39In7>pP$:r^,d-\n'
        'V$lflS@jY*EQhe3%Ile\\cCogks$4#N+oYP/;:Z*Q<OBRpKlWs\\\n'
        'D#.4!^SP/c:s3_OmRer1]:tA@Ve@D,eYLK.Gh>IZGuMV,2/Ets\n'
        'A^(=adB=7KP*a^sYa(2lD-\n'
        "@/fFKg1Wp)dS`m&`o!YK'8oRoJ%SOTMgbV/3@_gpIhK>&VgW6K\n"
        'oU$_fd<c^V2%:("u;28kU>nU8uXI>#>FnrS.l;&sEF3T<2_gpC\n'
        ';[s`M3)UggUU^)Ulbr(K^g>O2,9B6P?o-\n'
        'MTK*%joun]"FVEj4aoB03K*K)SeoTPN7.%5A(0KsWBR-UW\'s[5\n'
        'aH&8N*tThOB^15j@T`ID6-\n'
        'en,`o[O:S_ZlP+Fti`Ns%\\YL*`%+`8It58LoZkI@<cW&?2ZZ0Q\n'
        'AF&IdgVYGtAg_6XqV@Tk9h[`[T<VhudYFYsHCJKWe=j02+]S8,\n'
        '#^+34$sP>0bK74A.IYRY9ZkNYW+ZRPAi<StQh@nr/]&#pD+Fe;\n'
        "8>q;PF'ojS/h-",
    17: "Gat%__/%dZ'ZLMRfaciKY`hC,D:i%4P2dmEVD,GU1;dLp[h54&\n"
        'kLqJqJo#)Fk[;$g2XUO8*(R!WVBu,tfm7tj5JAM??`h(7CN$1^\n'
        "fh,Y<.J`lD,j<'<rD=rWePC<=TBUt(WY\\$C:If2#fk$r*BY$'Z\n"
        ';EZ:eZ?fcZP"m$-\n'
        'XeQ)3#K#lA]s@Xk`/]Mrk5M#.9i\\>dh:9DfFY6Z&s(dLt>S1$6\n'
        'L2stFDA#Pd6WjAMRU@JpYdi6$AkQuO)r^3)1un0@KT=XD*f)-\n'
        '[Y8;-.+qIGskXiYO;f!W4aUlT8eSJIlhCFifMt%K[2*-\n'
        "irA\\Aut^3k'gk(6Bd+AQiG_WTGWK](ao[MliD00\\A8VkiXYBMT\n"
        '[qQuK<T(PZo@A"$c$+nr:3bhPO540,HoKl%@7+it(B,iq&.3=/\n'
        "*97:a4B5pCtR>KN'^&aDF@R%qa_!2]nI$&Q0JJ+,:ud\\W.+Kpb\n"
        '/?aTMJBGmgs4%g%tX[-\n'
        '1YZT%TFcHVLTuJD(*pO\\_R3Qb^H<BFhB:T\\HB#h$HI4g**e=s4\n'
        'm0J0*I0>mkVq-giJ6+TT1%Elgt;!r(uM?oH0O0%IO',
    18: "Gat%__/%dZ'ZLMRfab^iqDR`&Kr)1f-\n"
        "a?B[$=bU(#n/_8CP$BG98I'_gD^W5YhaGkpA[mrm*ong[XMWUo\n"
        'Ub^(pE]C+o@rN"Pj7hbRVl$>TAJ!RS\'m;k-\n'
        '!pNahaNkrOTf_PK/"(_U!aD^r(F.0U*/fG?l+Hb(885;&?9emK\n'
        'R1>gE<82`_5U/Sml_dNHV_^%KZOA).E*toX-/S-\n'
        "NQUG!'BJ%7BKWJP$E:8s6)O%,&?<JArN!!5PRLWQUTW/t*U2S!\n"
        'KB`Np*?NQpJuo<W55X[3b(CldA,Xj1I_U5]?*0UHGEFh;)ZL&a\n'
        ']]GjXCtg9(5?/>.ZR,]\\%$)W\\XRDmrUdqMg#`PBnk95b:F2h!s\n'
        "'ofu>r5GQ;K*=tsQ=^]6D_-\n"
        "Q$J4q;BAKk&@]+@`(5F[l`Cl61<5G,6(S8@'e_9uPn.!m$>nML\n"
        '3-\n'
        'euqrbdUI;GprhD/>jAGA7QprpOt@f7+l9H%g`h]j<VftIe9*hM\n'
        'XDm`bDRM/lW8Qj-IYm_jU64DMd"\\u(Cgt28WSf_$kMm-lBGU-\n'
        '+98Ahtq^0mu+1TnC_Nm+,7u!lYVVq[\\:\\TZ2>f4LE";Vjb0_Rm\n'
        ']0)bi;5mEe',
    19: 'GasJOcV)/0\'ZUA9o\\b.B$hW@XSa5"`XZ<=&.P_B`,\'ZpURrfV8\n'
        'I^!_<JV)a"1]G.d^XB6dpcUJ&-\n'
        '1?9=99Xa(IZ>m^Om9;/7Pg[aSSL&/(7MLHf(`\\rXA68#!dj(L)\n'
        '%_s0"(l$cJIOo,\'.XX2N72C5+sH.3#_F.o=sJ\\q(*ea\'"X+;=j\n'
        'X<,VHHGq3L&.^&pU/-\n'
        "7kW;rmA@XD!iXU6;7$&'K3$jCsU]NhS#V_+[#b[C^1I=cg6N7\\\n"
        'H4bI;BEQ=Pu@"WD?RP3>FY?j3]LqTL,nhDDGMBF=4+C(1>PHu[\n'
        '-:oU0Ur0E3*ek?B9+I*bhl&R5^BQa"5OU:@@d:s4sB1n^85#%@\n'
        'KSd-\n'
        'V\'NQf3UN<g@R^g]!i0)G`7%Xm:*,nHN_#4([*h:p"dRr#;tCDI\n'
        'd`kGq8-\n'
        '*BHPC=kl^+WTEmQoNCbJ)LB`R[sJk$pFm`J!mOb(RNk:;MUlNX\n'
        '/QGZ-,G5lM;k^4D4,_L-h8)M2Y]bVSWnJB2L=/qA_fcckgGKQ-\n'
        "Qoq@-%23sX2C>G>RKc'<Mn:mU*UL!648oCZ>6\\F",
    20: 'Gat=jcVN:L\'ZVR1ZlQ[D_"AjX=P-\n'
        ")VBn76P'ACg_<1:1N)amHe6FG6BD:slt8_ZD;H2m@24*H'<[;X\n"
        "R7H+#qdn+fKECZFm\\X_1PDfu>&(/Qh`+!oK+]T!:NHol'Pfm:O\n"
        '[i"hWcJ%b1ob-Ub"g8i80c+<^`@^a]Cs$H*#M8(ME$#eILFT].\n'
        "$_rW\\`8\\e#\\[PR)h`6FMb_462?4I#.'9#]d/L9TXkeZ@4o-\n"
        'YjE#PqeI/X]P%H,@km?pWf">@o+:,t-\n'
        ",`CQ573'#5n=Q3a5[#7X]2-\n"
        'RH<H%]U!PGG;25^`^GB)nBaH/srD[n,)Y+0E&(HtO!]S7%rSB9\n'
        ',MI)=r/t4&Y/C@/S$f[i;S.\\.^m&\\-\n'
        "#9g6n.NIZ?&PVAW3U>gcp+p7'rEUi;9./'X+J<7MS!tF:9;#\\B\n"
        'C,>t%`&%.9FMo@*IMj#Qc$u285Si?M!=b4)i`-RIQ.e-\n'
        '%e&d3<9<[%_,7h[\'%gE&+G&PO7EF]S76"d4itT/T?OY0CLJ+50\n'
        'FHGKcT-\n'
        '<J8FD;b97Y+2k0Kk,C8pVL:0;BlaSra_sl7^0$;$rBP=JqGp6Q\n'
        'QO\'Lh!LWTY2pN]Z:o25QSfV;D2Ap+7dDh1"#*S1pOEWlZ66nt\\\n'
        'p]qW/)d8"nRTr3>1Zc\\(M"MlPb)o`oQib_FWBu.I$1R&OKGo+=\n'
        "=*YeC8iAUtl:#-7`);GR>lgrS[lD'`Y-\n"
        'nJ4+98=\'pX[r[)Xo5!Gaf:nK\'.j$X2G`[jl/94F"IZa<INuiQ*\n'
        "$Y=Nj!lkj@_4Xl<WWfBPA#da`EJ7KuXLF(;,#;W'Ug-\n"
        '(Kp#\'QsF*?Q[d!t[t),P9(P36b9a6b1;OHRk^!ApD*B4T11B"P\n'
        'Cm1ksk<@-sSW?9b.GW6WGtVO*rB]R-XP;!+`oK3!6R--Nca)pZ\n'
        '\\XUkd4q*4AreO76T-\n'
        'hHiDfN*;+5d!k>Wc;sD!us,!KY9k2CAY(e\'V\\,_s&01":/;Y1%\n'
        ']C024<6]*JPAEG;J"Map1,NZ\\K7@1!@#Ck5IYf^C`BXD]ijdbs\n'
        "p2BK[2fIS`.IRS>P8<SISlKG1[eC8F'sABXa%`#2rt:l49Aohb\n"
        ';K\'^Q&gY4uioSa11"FS>8X[@B7A5m+jlZ<hp$',
    21: 'Gat%_cYq8d\'ZZ!m"GbfWI?cgW$JPDkP9lPr+?#q%\'%.=r5fc]j\n'
        '-#2.58I)E*8T7)g%J0U/a%`#LESrA#H-\n'
        "bsTo5$qcHft.Lc:OuVn#Z#U&H'Wb?I8r5LgT0;%rj7Kr36Zdcd\n"
        'J1G>Q3%U`gAO)WLOjSCBu)sL0,aA7&Z8POp(:9G64DtHrp/k*>\n'
        'A/>TjJn76-\n'
        "sjF\\9s[jY;)<'jBsij?Wn&g_h?#ufRB1BLX\\YJ9%AUT>Hl!Gb!\n"
        'RD-5l6[q]`5VS<s7"u<)=#bG^?1.RB&-\n'
        'O#lZQP&#dIJe0*tAe=4Xj<J5/`P@1>1rUtjDe"]s3cm8CL:^7r\n'
        '._Q72H$k?NZHtXYM57"[#[g["/il;2q+)2E:5M^`Zkuu<VpaO\\\n'
        'CjHf;lFc)(o8=B_*_M=1s)oSu(DKA@#C^jfNi6@#9]IU.^,Me(\n'
        'Ol(!4!.9NI\':\\aa;Y-NHL-Ams/U$M+#Fd+J8S"aXlfs8b!XnhN\n'
        '&%[Q!k*^ZQXdK4Fq_Ps[S`&PfRQKE^9E3em=rp2D`>Np,?d_Cs\n'
        'WJehnjLnDAA.D3Zi*K^B=cOG57g-a&fS/5Qm^2<\\s#i7-\n'
        '9T@tO=1WD7*0b%A[][.k@NCMQA!cKo=?&s5b6&Z1!Z3W?@Ldc-\n'
        'tVOeO6VEH8d+gtkL#Du"km/',
    22: 'GasbWc"kfo\'YoWEd6m0+*iI5Y9$(\\/Cf4<t/rJ5c=V)<D8si:Y\n'
        '\\tSpD8_jL`oI.r.nc(J1AFi)Oep!LoR<eCN?[4k+It*OQ.QLq4\n'
        'JA`mL:G,0<.h_G<r:r#FK:fBgjTYZf.W]]ejB/K:q^5jhgJ*^P\n'
        'Xj/"2jS7;GX3Gi#H@[2336-\n'
        '8_JZ[`_F>\'^I9u:!^^"9_(\'\'@(7)FE;::j*FW<!;PH;OX&`jF7\n'
        'G%(8>taWI1mjlP\\MO^jQ9e$J5rZPcT3<j"?)>FjF8Z=:Sj9dO0\n'
        'EYrKgN!@_`)_B@M%1.VA?D$,YGcJ2(rr4m[Mckd%:+EDKb)djj\n'
        '-rm;An?#6\\H3\\`H3"QZKTBeCq`ubmquH92Xao5GHco0u$h\\f<`\n'
        'JgRd^c6UaUW(a,X136qQpgFZo"UQsGGaZq@OMm/WH).<]/#&)V\n'
        "Y@2FCOXEhZ9Qbh9$i(DY=,U/;L!O9*MT?AeZ<:89'8Reap:A[:\n"
        "iR?bD=hR\\;SaV<u9t+E@,A!sDroUaQ3TD&o)u8J6g.?9Vg'T@S\n"
        'O!PIRhg69%&ieaZ$J/$bnA,$CP;b"U40q\\<`O7@#fDlHlM*-\n'
        'ijJ[HW#<\'6I.JU"#?P[0u.aEGH0ttH=g+1Qr)Bg*0?!a7,o/Or\n'
        'W,BT(_Q',
    23: "Gat%_cYqMk'ZV_hC--OkDEU^?Pn39/'LDj%E[XWY;,+i,C#,XY\n"
        'SWHEL+<hAM6Q;grg?u]"q[<.Zb_[!h"s!?%*8AegTD(_CO4*J]\n'
        'V1Vb1]JQI+-\n'
        'MX?/3lO:RMdPJ_:[q_\\o0[dG^<&e_if+3eO@Xer@eG`29LsUug\n'
        '5(oR"=5Y512*j3M44#,N0LUhFqM*eQ4ca)6,ef5SG:rQp76jnL\n'
        'UJJ,>"BDBlt!Q:2CV\\27@6>@k<S,oo(o\\QXITULGZ^:Ha!kFa%\n'
        "t\\?>bMC>KFUJ@`SjT5rd[h*2][rW:`&T!eUL7()6@'mpGonNY6\n"
        'P3d1AEmH,43>[7VWFa0WQDS1[]Kh-;F4S"-\n'
        'E<9!5=A5MV+i=/;+WEb.c/T;6@05OYPojG^BF,&eKDYqkT9>j=\n'
        'KU<#+n,\'f"G&-@#Z1j@`&U3nl:`>mi-pX5]F\'uj(MJFCSM<CP<\n'
        'lrSu7M(5(3Ye!P$hZRViu[&c!/;rB#Q1BYdr;R<lZp5)j",L@o\n'
        '>3[1Z2D_dVk!+:-i;soL2b-\n'
        "UP<hB>$3'9\\KnL`N.G1?Pc\\j+ZjR,]ZmP/[t.;FIL](Y;B6Q$!\n"
        '\'a;>p@",G00jPQpD7UbN\'F4YVL\'JA$=H\'7^)ON*cN?U"g,_sS[\n'
        '4^)eN3VXr?"/u[\\U\\ll#$\'gjp]Q_7QkC"PlaY53`oR]bU-\n'
        'X42)^YGPeC)sDO4;fC/Z9/i<N;/^`G?>VQgDPLVa2I)TsQ;r./\n'
        'Pa[n8dmYOh^B.V"nG',
    24: 'Gat=gc#;&r&B-\n'
        '/^(0\'t`lUlLQ(*p?Kg2RTJW.G@&OV%.eAD,7q7SW6J8^QUM"S]\n'
        'Sar4hT2*()]mca#<AH[bkc7J!;IgM%ZW?1?Dh?*98R^J5S!8XK\n'
        '2[?iJ"4Gep#/(\\gE5"4@`l]@\'`=;5S+Uh_H^^K`<DRC5N$0PM6\n'
        ':`BZO),#kt?WOL_k7q++f!*!()umsDIJ"CYq5TW1Y385*)lFum\n'
        "6P9TQEB=9:9+Ps0'X(I<Q0Qs=/3%1iK[fdAI>@+M2Hcn5h@p,o\n"
        'R4koBPBYTh]Q,H:^$N]iuZ_9lW:0s,N$)i3OTmb8c@ZV5q=K5#\n'
        '6Z(/6J%[`N3TT]2]G7h@(c*_b6&[3E\\)YP7\\/&F)@f&g!krJNZ\n'
        ":)r0SdO-uh*%a'2i?D)-\n"
        'S:Q5#gOM!8X6ortR]N5$4I2jb7C^q1h?5(Q/qY^KReZ[;u=qEn\n'
        'CbPL\\9M*Bl3BE[?M0oW"@FjAWHh"7hXqQ/<5c@?lgUr9WPUaAo\n'
        'h,B\'D[?r7p[_]Pbc6rU:PA_g^5+qZ6LP5sBs.f$""/E\\Gb60T%\n'
        'K(n0*]5N%WqX)]\'BF?5Nou(\\q"5)gYfk)&1K*(C&?iLo7c&p)h\n'
        '%P!*o',
    25: 'GasbWc&WJl\'YlYIM&uBMBs2I(R"Z!d9F$<5$R?\\IX?bQ/@q)/U\n'
        '*G?I8Qm!0>,b!r12sW]oa`bf8"*3n-\n'
        '1OX]CqKq](9n/]5rc<OS8m.b3aau&=pl<S_Lb.%/<V`W.X0R,K\n'
        "5H'WHl%'V'&0-\n"
        'Na%?)ci3;Cut#I:\'TU$*`F\\?RB3i*`l^Z!Ciu%RtVp>kAB",KH\n'
        'LkC;U.4;o29b_RD(?PFW/;C`V)NS;5Es0Lirn3/i`J?6PWk+J?\n'
        '/MNjB]nJIi9ck^\\2@PV:VZ7Sb*W+gq&%GXhat6Spo&762T5KIJ\n'
        "'/$'D7b*-\n"
        'U^*"E[$s`i#jbPVZ$@ZAt\\B#C*4h2?\\Y\\QP%0@(^o\\[Q_)G262\n'
        "!ZZ_OES#r(frA3nQA:Ml$fY2]YFDJe3XRZ8qgfiJ<8Hq'mje@N\n"
        '<ct%=5=e[G&S\\OO)g=F@h&IB=1<=3b(jeitX,d.cdg.ehA7%9Y\n'
        'r(6oLds448(/H-\n'
        'U[`q7Y$sX4Hl*V3_u\'r(Q?Tc1VNZLB$#jYin=:[pXZFirI"Iu+\n'
        '@Alh_LmjLY*,ui!p0*L!m/mE0pJTX-EbkV2@U.c)5klj#-\n'
        '[\'#$V=#8U1DDTQ,"lF^h3+qLGeaC!3@HWB5&fl9N,l[(05Og;Y\n'
        '!u,CQcVPc0;SBT@[>?`fb?Pf6hmM;j7N>P.]-\n'
        'H#Ie6K%EO\\\\H0KQrf;iBdqc.V5Y(sX!!=pD$qb9*t%VB82HB!s\n'
        'F"<B]4>YI42QP#kcD6H;UG2%JhB,Cjf2neq\'@;Vpm#ajpT?`d;\n'
        'p00nbg2Z',
    26: 'Gb!$B]5QFX&B7X*7QUb/MQCHp6P:5r*k)!f@&\'nJE/Y""JPJXQ\n'
        'U*r[B?BFA=*a5q_[^,pO.8"c#VjY-\n'
        'g"&=6"pZ$H#q>Kg7MoL=r8T>SVP)82O-&-\n'
        '5nM>/MpIu(;fUj+A=LsN@_Jd9FkOW7b,:Cs7hMlet>"2nOQA[[\n'
        'I*;Di)kOk6j,=DT4T-\n'
        'JV5T44B\\C[Jg`]4X5j2Q)]cSGXQmYjOK"s&s.F;&Q*,(hsT(<:\n'
        '"h4NW&1fd+fVlYonN1%5UssS=dOIu*:FQ`m\'_lI]*,Ge>\\o;#]\n'
        "^0oGB>_;\\KTEF=l4/og^'e.^9unE=,`mN)ImII2@s&`p85,&$7\n"
        'UGaW9=oHAM$5^G)=SKQa5B\\)N49PY8+8QqklPaa/t1d?go4Ufn\n'
        'bej3YlG2*GR)4XP_F+gHKVk\'oi]5:+uc**o5+@Vj`<"Djg0>]j\n'
        'h`KR_O"i$^bPrOC:hufHQ5@d+Q=t1\';4Bi\'[Vm/(u5!S!#.Hdb\n'
        '2fEJ?I!N+!$Pa;5jX)\\554.9\\!cDl?n9F-\n'
        '/0P*SNC.u0<%YC8]aZ&-\n'
        'b/!2%18Gu75\\lW0a3QG2(oA0YjFGLtj2cbK(hF#NdT@H#*fJP-\n'
        "N+4?jV,=guJ[@1&5ACOkfomf&dB#Gr9NF'K.#MNZ4P.i!6SkeZ\n"
        'B\\(NeL.2DcVP4p>QJ3:M4`FQ]kp,S=#EIZim%3(QJZe6Lcg"\\\'\n'
        "YL!'B`]=m3RP#C<H:PFLG2LZFi1g/h/8IB)",
    27: "Gas2G?#/1K'SaesY[-\n"
        "n8[qCL_)hK#Y0A],q7TW%p.',*,)aSYCg=.4\\<Yjk-YheV_g)o\n"
        '$%S*]pN8_-s$8308%hBQ5hH[l%g:.h)K?A)CJi%Jte7-\n'
        "8_?IZ'+kieKMVcXf@hPFW$H$-\n"
        'Ce5LJo$WRA7js=QNX)&ot3L$7s=3WdAYqCJmb6r^-\n'
        'ZWaICD.TV*=7Z8n&`QCoX3Ifi9@et^NtPLj\'7i"itki&#RP.M%\n'
        '.t\\WbJgJC^\\6mA=V"6Dti:f)Y#\\JO3WQ`XtP/kJmjhj[e9\'Z29\n'
        '3Ol<PMs<+X"I/6%Jp>Jd;DlC*5=ql6bUkL)(8$)gg0[,R2i?5`\n'
        "1=qF<eH&K2[hTg#>S:D/]Q!85X'_Y`(V87F;8jo'SYS#fopqK'\n"
        'H"?p;[<`+/sfR!9.p&6KJInN@!mbc\\^n&iWa#G6RfcO5rA/6*l\n'
        '8p_U%?i9%*)aV1BGER!jd)1=,BpqHh>A>)\\>cftYKlX9egu.YD\n'
        'TDL/j\\PfF>=J-\n'
        "0oLVN.`A$1l2Pm&E8X7=DTes)T4r(=2nV]a?0thcS$_e!YK%'U\n"
        'p0ADPPC%t?[@`(c<u?)<YXKPF=@ljO5k6io7Qg(!C8Jbp5GX#a\n'
        'o1)Te^h\\g(Ar!E?`Nt!2U\\ZMN%@KN*6j#g\\_trAV,EMG[Yg(+B\n'
        'M#I@Wg6(j10.D,/Y/>bWOfO@l.U0ZgEtH6f<S]6[]*]J+gr_b;\n'
        '#UJE.518',
    28: "Gb!$BcYq8d'ZVT''-\n"
        ")2R[M.Xl3Nu4+bAX;mU]SP$UCn2$JgMjlB`i'J/a8KnRKRil0`\n"
        'Nf7PAY*SN=0)@NoTlja58lIO4!DLUE-I(5$G0j.JT)_[_O=rM-\n'
        'o9+VmmCqHrgNj=#l)V"$m%m."l!L?HLQB4+8`sUVY/V<j[OkX/\n'
        '^=*f+0lRGB\\_E-\n'
        "V^6SJ]_$NfC],_WUs7&b'?W>ecb6X0_.=bHKBQQ7j+?ZJIVrCH\n"
        'uH\'#j[QB<D^"D;LPI?Jf_A<(H7,PW2NRR3hoSum5^S/&g-\n'
        '(#3+/*:JW]]A5)9I\\lD$\\/aJtWM<db=o$M0;@2;hWK^,6otF:M\n'
        'iO[q[?%Mr_<Cr!Vp&CRH%28n+46(*C]:]5C6Tc?WJku$Eg\\hgV\n'
        "sq?'>$DEr96_a_&StAb]iiu'Gn`2F./t/P2W_CYY9sh3@d$Y:`\n"
        '`@(VN0SmMg8?T]Q0NR<OQ9Mjpc]BQPIU3g_B\\^lQT@9/1tfORU\n'
        'U-NH\\@P>--S/D?l>U*o)4J,_Afpu@Wp!!5HroVgHBO--\n'
        '[5eq5[B.+*djC`4pb-\n'
        '1:GF/HD$>K72,5,Eokc?R&kkh5O8["?6Z`VB8Sf&La&["2$j,F\n'
        'b(m6-YPq`4<fb=^P',
    29: "Gatm7cYM8h'J:qJ41+0W?dY\\h_m*dn9mfO*Ch4lC_0-\n"
        '^n&S+OPbS!"Uaf7T2m9R3$s6jL?2@A\\VLOHVtVb^*\\T&/M`GFl\n'
        'NlN\\i@VB1Z.#\'JHZ3P"j%j50DIfo!c7C0@YUOY)FO0_*MM,7Ka\n'
        "L+fr,qrGE!d?'T=P-lcUe$_]VSqcjI)]Ko-\n"
        '^f:_20lgiuNn7\\&c^g/Bte!DMF%,4ui*rf`d.Hb"T\\>(O-\n'
        'i3qR;Ye;eAS%U_/%TPr;LWLYLB"Q(,O=rc7[RQS5;ER^K.0*hW\n'
        '#&Ym^mn4=X/Va?qjB,ta@eB(a9Iom)sSHd0??rad8pn8,gS3dT\n'
        '6L:pj#jfiWRScuT3;sd1or)M^JnK/I439IONbN3ssNd&K(fuCn\n'
        '@.[G(?BDE"\\1J1d[nY/R\'Q9]Ht8[6N![(\'tp]XU+kf-\n'
        'A>CUNeY)^XrVW5gGG/fp"(Hp$Q+SAkC#5c%eD5VWCP*oVh\'2C0\n'
        "(#kl'GieABeN-f'HZ0cQ1-MGh`lYTB?WcaD)NT23HnBot-gQ`@\n"
        '_YXJf@0CNc4t?Vc&KMXI#`#O8A9pH&3Uj+\\e@pET4S)ZL@Gj1e\n'
        "lFQTO'juP_Ei8`iaNB4VEj0i4^QtdeNuoKEaU",
    30: 'Gatn"cYM8h\'ZUSSfFGUhqMJ\\J6M&)qlGTPVJ[1Qg"U=:(cn3>I\n'
        "dY'TgZ'.Y.%CWlVLM?eWT&dE,ZC](M3EX`,k4A51d'q`4+123G\n"
        ';d!>/1fs8D2-\n'
        ']P^9@Zi2lFZnm:?=8_W)#Ai&6\'Ua_k/%Q"fO/5J=_Tu+[J_oTp\n'
        'cN=#MN/iTFrE(C$Uld]787^8k@;=oJJ:kL2a&%5c-\n'
        '[f3,7dn%.hd:d=`$b+@M?$C]]QLd-*-\n'
        'm<:6HC=V6C(#_lQ\\+N2\\PDUE5m(_d[&pHuAl.mgRf;:s,*oWV?\n'
        '&-\n'
        '"%FGe"F(A)s\\"QSfi9f4$sRf.*BpZ.EomrT!TiWGp:5YLP@etp\n'
        'Bd^LJE"!DmYgG0\\7k.8/2+:gLX/$bXD("0q)cRhPfpng>$3U<;\n'
        'Hh0%H:dmUr<ECjFYSo$XDS6J^*uO,.pp$\'ST:+A@MV8J+*[q1"\n'
        "I?Q>Q)rtVR&jdg=YN'@f>Gek%E]LUN/r/3oKXIWp`dg<Y:#N:0\n"
        "]V]oD*1BZq0cR59RO'jVB9FAA$U]:`PA3*gZ5S0*]Wp#LFLPg%\n"
        'p?1lSQV7)l^!]H\\$OS:qZPQ9ZOi9Zi21ri:V`$S@%K_Fb?:9SQ\n'
        '5qKIq_rYCW7,"VFQ9]d.=\'F:D2YjiNpW?&a76+qfj/he;K?I"O\n'
        'S(4"h!%^lnm9Y53$$W44homZr/gVc2kW!L6_!cO4((%W>cUY;-\n'
        'Thod(:2Lg[=/3TROf?',
    31: 'Gatn"cYqMk\'ZW:pC-\n'
        '2(El_?JeY$DqI#qZbkD;*?)OXdK]:=J8@!uXZM`IT@k9&8=4H%\n'
        '4\';]@m!G!nC\'5M]BM,^%_\'KG5U"fo=&_$fdUk7-\n'
        "tIqE)'bbI;(-\n"
        "mOZX;]XSFY8e+MLK]W'/JF9+YJ7!*YO20Eb1[!C0PMo!H9cZDQ\n"
        "`33@IT6P\\JfT&tYJJoS]TgB;F<K'e]m_PjkhrCBXT*LSS7^8#T\n"
        'LhP4Ms"W`\\-cL<olC\'GRqaEkOOqoEr+qpBaD/Q.;>Wi-\n'
        '\\M4M(U@j%I+ZC@CShK0hFQr<2WZe^Ee3O,\\u)5CWYZMWl*Rp8Z\n'
        'D8ejH"U>JagS<LIVD#)=k[%pQ!f75P[c29RQssKm60s*2/?2Vs\n'
        "qNtGQkP^YF8o_lK7i%^V(d0i^'IoQ3[>48phPRTB:22]-\n"
        'N3I"EQV8$W^S+H!/[a\\s1bdKqE-FKQVM?.:#;+mpV&2fsG0U(k\n'
        'WT>JK(h\\TGc*:[-h-m_;F-\n'
        'A8HWAg+oj!2K*BFd/dd`$Pc"cfNI9g/r"G?F%P78nl9Q]77Z?]\n'
        '`1^.=5j:smWR3,:n3[d=H*ugcoG3@:19`"l"]AG@?Af#?_JrfE\n'
        'ObVBKB>L#*LYgkUfe\\s[af!]Dj9lSFoZSo+*@N]L>f>s=dFY#Z\n'
        '@=dD?-[X026qEGb^-QW',
    32: 'Gatn";+ne\\&BBQ$oYL8bHBJNr\'Q\'&:gBtiLk`ApYoMm4);E)%,\n'
        'A*p&q"b"^dnb\\bsmHg_.KDV!.mW+Y$&))@\\INB12M9<IjU6@k3\n'
        'm5>t>RngnW3.)OGU<GQ-\n'
        '6JP5s%/it2*<^%B\'L`"fHltc(=&r21Efs]h8R;Ulq,*AJ&Q0b[\n'
        "WE#D*5m7rY>qC,MRKs]*G&r<b\\XBF[Q&uK_PYY2DdTVM^J/)'^\n"
        '>MQH\'am8SA.HVr."!"F@Id\'uI:r`E!aO`!WR]B]q;T6O9@DVn0\n'
        "BJk$2KNf0ZIg_RV@MZ',O8:M\\nZDS+aF)Cgj]g-\n"
        "f4.A6Xc_^dK_/.90+,:Df@FPehTRI:O('j`2h9tH'a*4]>1E-\n"
        'D3U0$8!RuPG:pqlY!DP-\n'
        'a`Q1\'_"i$l_o;GO6LmR?&U2Yc]GO23iI`"&>9_+P\\,e]B8kY^$\n'
        'YGBb>/i")_qk>D?e#%:!tdY$:3iZ_?]VdD_Q2%G`_n.`\'&F[CW\n'
        '4KX]kITj4,(XPB],uN"BGXFV0Lp0DJK;_>',
    33: "GatU/6#54/'J?b(47qCq$U1qm`Js9)B`fZ8Od.fK2R^I>UC>h$\n"
        "MG5,5fLg!&#2@tCC&`BTCrc(c:AmH;krn9XT:VX'm/<OBn#UM6\n"
        'mO_##b4<L\\=lPCYns=as;gt(RjfSs3#A&jRk<YEo>XOqT(5uiB\n'
        'F^R@<[D<W9!=VdA6]I5"Y3I`!C9LK)7U($>c1\'AUBc/f_f)(_u\n'
        "3g+D9[L?I&SX!(@XVp]lj>u7h%`:kbAt.(*;0AhN?#K$d'fHI>\n"
        '.8`Ub?)o.;E,30b7mdrmY1tW<j)6=+VV819/]/s\\d*[)9NJ=,j\n'
        'H*&.6e5*aUqQfLe.eIXDj@s"Z\\"fPPPL!gUEkhAb+d:B-E^-\n'
        'b/n]EB.D\\DUTM?:GHqi<1Z9I,#"ne"d67(pMA;\\?;=/C=t6$iS\n'
        "S>2qM[7,KlEtpk05=NXU*R_\\k(P;G8JJr=GBAb:'!ZMmW;WlMK\n"
        'k3rheY&TSSY,?sG"O+U\\H?`-\n'
        'H19H`"(bHj+4"$9s&0V=8Tob;_Qri#rY(d2+bIY5lEH@$ifqaF\n'
        'Z*4THoDZCt49LT*$8[+E<?6h2jsX&?c6+39I3c]BIgr@4jfa5b\n'
        'bQ*TnJHb4t.Tg4]tNu=3DF/:GS*W:K?[?#Si7tPu:naYEO2)PE\n'
        '-5;pnH;n;5BQp$`1m2OWcIk)6X_H,c9F?[ldKpJCc&!4H^7Y*q\n'
        'l-\n'
        '\\b;lp+[X/@0GN@C$q]%fDA9mRR*Z_c.9?X4#"hL9u#pnfgACqt\n'
        '`o-(A%g*`6$D[gNiL=EO\\ha)JE\\/05P!f$k,V"k6il<T8',
    34: "Gb!$B95E9I&B=lqBFhZ:3^HTj3[iRs[cA';#\\b]DTho*B-\n"
        "tXcbA78VVo^_iTB^`NTqf2Jg\\p@TAfLlH@3tKSSrd*pl_='U@Z\n"
        'dQ#J_2dklT"f_"4\'[q3s2EmojPTcUr^mn"2rVuWdMQJ<i[e,ML\n'
        '!j(7\'\'hPp=F"-\n'
        '_A4[b`O47GOigdF(?/`"sAPgF4`u>I&!Oa!LH3E3Ojti+NE`o?\n'
        'mO"Ucu#,rLD7D?pHCCS1-riiI2\'*Q>?`4R-\n'
        'paX_!4S#@a>RbR$+WIB`5kP_B/(-p20FG,6Mq@/"lQ`d[A&-\n'
        "Qi/CL13!`D.m'60]+5.kju7HV(;7BaMb&m65R:U_f/8P&:5SJ$\n"
        "]0,JGD30#8m$0H%(4D]Sk:^(CqC<YbMe^9kaSh&n7;<']4E_Ai\n"
        '.U,ciXn.)#<\\["qis.&BDTmXFT$Zpkh9ghH%6EJ+JU:#,(4.F-\n'
        '^/c;,E;aY3Xh+L<6@?V9@MLRk6/!EY0$jG.H?%!Za]ToPc2GK`\n'
        'd=QYe]-\n'
        '?&4ib_"UOY7:[AOdqbi)7&"sE4kQn?[V,<r7:Oo=a(!kj,dOc#\n'
        'gAdCnqb4([ni6_\\_^u+V.OZCG4dicD-D%Q-Wrb.FMnGI=&h(%-\n'
        '\\3`7=a0Ug3BFf+HnH-\n'
        ",Z3MWP&>'/U0KSQ_Ir.^h'4NJT[HF_,$@a[hi23\\$/`=R'!gN3\n"
        "R)$A'H/V,s'FiSoFKY:p`=<",
    35: 'GatU0c\\pLB\'OI`d6MJ4GLUjp;M0<?e\'h"a;QXpmIg1sh<alE]-\n'
        'M.@6CKGN;=gcGCLHg/aBa5E7Mkm-LCpZ$VX)rC@lp%)8N9V]d8\n'
        "CV6?m^V%BuZG[^P6X5'V?U^<rO9+lS)Dg^Z+S]cQ+mitW.`h=F\n"
        'OZI/<%7g\\R#lr$Jd#_nM"(p5jGCVGND(+#3nW>e>@\'HhE\\n]P7\n'
        ']lS&_e<g%;L-!]d;dM7"m,O.(jdn.[P>dOJQl-\n'
        '*/.q9@$Tn1=WjhP8%23/1Sl^0caXdQcPUS;C"I%22t!"Z;1WGd\n'
        ';-\n'
        'VWesiQ?GH]_D53*a.f1#E49G,W<=cImr&W9EG)l02HI_4)2=_n\n'
        "kab%cbX1R(hPPUqlI'H-Ct-\n"
        '3QEe@P52;rEGYTfLFS+63T[a$CqJ,,<?LfSe-:r$3>!D-\n'
        '@,(<]\'2@"ig#+<`kDAHHk&[qWATJ!C8"e;!9GY%1:6Q&t\'&;!(\n'
        'SO!bINmAaf2i!$#lr<oTK[lBmec;Q>IcQI<\\e2tLJVZMCO)fod\n'
        '(0Y"6k5`KI=o@eV%\'dNBi=H(.7uP/d.`gu[FD3iV<!^Pu2G/[s\n'
        'G!,5#7[8"Ss_72dPZFb,08>O^8="ecVk2!i9s\\qL9*jesFS+j<\n'
        "Rdh2^=%<'oUp%>j4.;,+!=fB28]k2,.CcGp)(r*nUVh`?0B5bf\n"
        'hHN$]%\'THW)D"eWOK362KJ4rWB763N:Ci;ib8j#SE74<+JkjL>\n'
        "6,`:4hno8l=e2]0-/L]#Q@O1\\#J_Yt#CN'@%",
    36: 'Gatn"bAPco\'S_N:"cMf\\j<V&SWClJ\\/pNR&"BC[SW^N[9:fYcM\n'
        'a2EjF8%)(X"VU07a7*?H\'\'%.P)kr2n^T?tL5NdE8e+q_nn[!:5\n'
        'W6[P0\\r-`AG!WUIU-\n'
        '%mN%).QOU<fIS$#q1O;ii2"X6c]/Pq&6>+j-\n'
        'g%,p<R:@C)#V\\$]-G<(I?*8HR#a+S;@&[L:,/LFHpaVJoa#U-\n'
        '+-\n'
        'M(Qq%V]pQrYmsumb5o;kLS*!A9jSu2!hGeJB9`cagrutEXc`55\n'
        '\';?d%k+P"HDD\\MCP=YA7peZC;fgU>X8\'nOk/1Xp:TMSGkO3[Q5\n'
        '%BK^hp\\"C*.hdj;ol89ZK,43oF&K]JP+<WmBDg`&4@`f4fZ?LE\n'
        ":pkrq[ST'LKKTN8IY0b3p(aU$8-$;+OEA=fBioA@Op_eK67q-\n"
        "n^O&rh#U[4Q;HB*bH1(W/Z'n;*@7ES6I7sRO0^ObH)eVf'H#mB\n"
        'I"*7N"#1C+)1og#i>Qm^h=TFQ]-]E]3!CQPm-\n'
        '%7ue8=1D+d^=sBMIO03n)t\\[VTsKkpTT,dCJHg=D`e3IOD/+4G\n'
        '?GB,"$B3Zt#sZR`Ds8la1noRDCZ`0FSf=+Q3X\'A2Rtbc^E4HU/\n'
        'k#uGm3G)r&h&N/17kOO>6d$BD*&^-\n'
        'S%:*T(KT4$4rd%6qMeNjJFA1MR$*GckEV9b@_DC]',
    37: "GasbWcVN:L'Z\\T*g()oK9\\Q8P1oP0<Ui]6_78*fWVUD8WV[4M.\n"
        'H(bse;T/ZA+f+MngUoajs2Ss-\n'
        '.<H8@hrm*"nbdZ]0Cef(?ba(ZN1+4&7cmC%=/TS`@ksB8V>EX:\n'
        'bGKN`(?E$k$t4c.a5NOMWct7TA7l.e,5]sNN[#:4Ba/Eib8&<F\n'
        'CBoljNRZ1fR-\n'
        "k'He:`<C&NJQK7^S%kLk`^3!ACh(Jnkf*eBXa2k[t&UPT$\\2.d\n"
        ')TK>-=t4>hCTL>m<>,O8\'r:aMJ)_F:V&"%)JH;`u-\n'
        'iUU^<[<etJ,))j?M%2jksZ0^mBN;-\n'
        '/#p$e*gO>h?+(FDnj`Q%^a:aWgk::3m_[rses\\p-\n'
        '<jtg`CUOfUK0kQ=(*7l#ZeFi<ejh.0>AIIZ\\%k7mjPf=S?pAWT\n'
        '\\_@e,0j@79Pb3_))BtbReg-"d16J>[`JjdQY-N_:nJPW40Euic\n'
        'To5QpL4:::A*t(hZ:Jpm@r-\n'
        'G`$chQD_]h?*a<]Wgg%ZqM%b*9+iHO;Bi\',"l,2URQuQEl=45D\n'
        'g2N@q-\n'
        '0A<mXJL;"Qn.@4RNPQ+)GR]gK#ZW[DSM`$%#A?2TLdZ_;S;r`6\n'
        '(8fe<$F"r@<3hFX%8c>^(bL[U::7kM]7=<EP2n\'"k?qD`)gf4N\n'
        "/h5#>tt,[jpOdR,/p,iFLjcYp\\]IJ]`'&C#C[1INMSTAYtMY7V\n"
        '1FtXPkO,k-\n'
        'G:ZN0h%l]9iE_0#!I8LoLP)=h=uCh;G9F2oD1XB4E;i#g&;(b7\n'
        'RHY',
    38: "Gas2G95E9I&:ak&BFhZ:3^FQ$Jg9U?LG!a!BdfrR_')WI-nB!H\n"
        'X47SLN[:\\jHe5CST@NtkI:sq]+WV_?G@pQ<a6rrnrV>20imP#W\n'
        '+\\FLf^UclX?D<,N-\n'
        'A,[dM=g+DC*<7m0NXVU!!W6V12m0d9NtI"q]8A),5[%BZVmK8"\n'
        'U4i\\D$:Kd1L]gf!#uOakjkZ3LD/N!!ja>u5"4E5Oc6A.@@g_$M\n'
        '+ESuL`EAn6:Mc:>+ErOeQ,Q:Uak&QVMaharduiSThAp_0T];]k\n'
        '`W1%#@;qZ_P3:\'(R2-*>"I\\sI$BrDp-Efk?n])Tn4pDl=S*2Y]\n'
        '<2YR6.m"+noc\\]#0SVW$G#Qp4:!5`Icl5P6AsY1,c$TUm]^eNq\n'
        'h-\n'
        '<q1I@;0$,R0J0+hNR]Di`TY"sqY!KP7G]KRd`k]C=dK9,O<b\'4\n'
        '#(oS=ZO_8VH\'@b@i\'b3(bpE"])EOBaGniYpCO5N#$OJ3G:FU\\\\\n'
        'e`_`06O4O85!*9HW604&6$RCo$]cE\\>"Rr;>VkQ`LFapT9>6\'6\n'
        'sBDM$Y>!o-\n'
        '8_Ba43!ZNLhMIe5mBEJ2Y0^&$M8A7hjq=i.ftko=Ti\'#&5"KJ!\n'
        "HnZ?X0e*s>t]5^'r$F4P?$;(BlXS)aA;G)bH48kL&!Lt$(;IQ>\n"
        'h02,tT&J3(,\\c-\n'
        'd$qZm>=]5uVXcWiBr1Z0==CFDR"sR6*<$cdPk[C&2YCO49S+@U\n'
        '8R6_k&gtT\'3\';c6d&A6R4%sIu"G-C]',
    39: "Gas2GcYM8h'ZUSSfa^13f#nPAk`WaH34<T]-\n"
        'BQ$qb(p.PoeNrgjB--\n'
        "?'&2'aVAofp?+4PJn+=M<SNuqgMP&aPqFL(oqUPI9HY5s!f%]/\n"
        'Xip?ImhN7sop`D]pc%#:JHR8gl?5QU;Z2da=I9"%U*$KDl+,)a\n'
        '&D[?++>67+sW$"oFM06gT,kIjJ%RV(`,$7_e=f50.Q`ri7R]Z5\n'
        "a'oBk2!^niTOk^!Zc_)eF+q%OWqQ1R/ad%r77SC--e9X)#K^Go\n"
        'Hfmm&@RbSNdnt8Y>X4gPmQcGJR:icgY*9p-\n'
        '1iKF`q8YG2_W(Tu>dLB\',L1[HI^"<*ir0di1aX4(U6X,6ea>.<\n'
        ",ac9Y$oKT?K2/RA5gjBeF#djdA3@U@SK]S'&aYo7\\&AiV;,9\\9\n"
        "@kn9R'H:n%7-L@6T[j:#*.6Bb-lXCsB=*GSblSM88%AX`s)J\\6\n"
        '0C0]?=fDKf(l\'o_"7-\n'
        '$G_Jii+a1Np;O]=^8=>HcLU9!\\:\\[a#]>6Y3Eq\\>F9nYN*gPq&\n'
        'XKH?sg^(Pf2Qt@U*XXGA.Z+6Ol]e,D-\n'
        "THgO/Z'l5WEJ<uZ:NN6iKO3(ZYTEDjdI*kRNSIZ'+ON(_CJV<n\n"
        "a_ma/3ZrsdV0kW5Et_8c^lZbU^#&'#q:h[k-\n"
        'n=#!Htn[RF(%d`+c**dhF$-\n'
        "!8p?>TLqj';JQ'<E53[9YLonX<\\^!:7<>V#",
    40: 'Gatn"bAYip&;Mcu#S+QB3bU0$7\':#IG%q=0&qUIU5UC_D;7\')1\n'
        "'<@-\n"
        '6fiu$"M?N[eZ1.LnI`3r$#!Y>ZoC+[pC[JUVcX36,69X#TdTra\n'
        '2dn@9k);V86b4r+LW[FG&J=>fC6td1[(2:Ad&T^mO1:0W1G:b*\n'
        'gciZS,d6S<G9%W%Q#9eVJW++I@Kn=8;cO#dt]u=Xj<Mlsp(BpW\n'
        'X$"9:Vs/I6TJ24"j"Va*<<O-\n'
        'Kt?haf>h.If%)oAk%8^L*4^,F*/+m=KO.&n27820U;gB??H;>G\n'
        "W'!J/SmB=5':apDuZ_P^m(j%-\n"
        '*h<@0.IGhF"0neVF,DH\\)q\'9&re&+cfVjps!a:=01Mq4i^khFB\n'
        'Z\\fU?43]l,1M`_iOXrZY&Zs/,f]5hQm1#\\/!7OkkGr3kYoss"R\n'
        '!qL0;N9f*<4t@%Z5jI2GBa+E39YQ_YU&&CBMjn-\n'
        '&Lj+lbE@cdh-\n'
        '!=Ir1]lofg6#_nZ!SB/#SDNf2BL9Y\\8@a*`K/=C)8X?N`^&EhV\n'
        'Lam5EjR";tobnO9IAfQ\'*79Cet@D$L0hdD<gHq<]&7>E_=a"<^\n'
        ':B#.JKT&+/,CV&7*1o3g9=jHiY3O^Tpm=XNsNpYRg\\=P-\n'
        '0FU*P,**@#gTbf7M*^uQ$3mej%3b6`\\EFaEs!COkCO,g;]i&Tg\n'
        '*Q[(2pNe9^<Q2)B3W>\\_',
    41: 'Gat=g>AqtE\'S(u&":ok:\'9Xa3@8p0k3)-\n'
        'sgM&(*!VQJ:B+o4#i:?&@/1oYKr<rr]brJ(,Hr$m(eR]ul+8$\\\n'
        '0$mIN>prO)C[B5^Gb!UD?-\n'
        'WoWNo$!rcD?LdL^kr8Tq+0^ME^ot[g$p"HtU.TrI=^nR_&;&en\n'
        '67MgjJVs-2[4GH.$+)#NV-\n'
        'D\'2]*\',k.fqR2.2,Q""Dn\\!\\D]RR\'o%mE3k)2=7FJT.[Y&<]E\'\n'
        'FAl.B&h(g$K$sru5CJ.VMJbmLX(g<.@9.G6h"c!F%n"VcH[$hc\n'
        'GgjiDRu23s9;eL7g211IuT2D1^1?0D.DJ..$ZS2cE7Nn1VYUD=\n'
        'u*5eUl_I0_G2T6!ZfJ[AFtHJrSH<9R`>ts2#)sVUm9=pt;$OYO\n'
        'ue2%b[$`8Y^Z)5a?t::;AlmZY3)@E.ObpHi.FF>X(CFpmc^W.2\n'
        'Y$l^;Y8nA=48"f1E9((*oqUZQu0/2eDS%`B0?NI#jK?"K_25U`\n'
        '(43#=Wo8OJi6B.^\'=^7QJf\\1^5*("i9^Q]+K=Hdc0V.2CFnbH!\n'
        '`4+@$)=[5o.$O(BiYM<Kfgr<Y]le5)H4YkYtBF&j(G[q5R"8pG\n'
        "aV>ZNk=0XWY?rX*'4+bh9/d*]`X#ZB9VBCd2l9J-\n"
        'Oq@b1X^nNtFuRhJkN2*67_hB,D9=5ss_PK;%HT#e>C(-\n'
        'Qs[$CjTJVS</]B&WZe*&<Aq[EU+E;[4:#',
    42: 'GatUocYM8h\'Z\\C_Z5n62jSFUOBZHk$Eh"481kF&>OVe;gFVHiu\n'
        'RukPu[aR3k_04FIgAa85n?7T>ZmUs-TAKIXY@Qs3lVH(mdrri;\n'
        '>ImH2Ire,hbbmPm>?q+>5K"jt/Jl?Ll&5Wd"9>#5-\n'
        '^Gu5jTp8e@i_+DX=Fr;&jAE&-\n'
        'rUkR6IM\'mA+FAdR1"8eaK#TWY-(Za*4+>",cF-\n'
        '[AmGfn2q<Vl]W1U]#"VD\\8jZt+;8i^T8;;mu6B3CXgf]hkRKSR\n'
        'Tf>[b69\\$j,!]G^McNq%525Ud>$"ft*JOpHm8YT,m:`XpXkVR&\n'
        'G8jnknZ#23:C6HDR(K136T8FfU*mj:tDcE?q2,q1aHB?g+DH<G\n'
        'p#_XHhs"@9VroRfNDW=/4(a!H&eJX6prm(`-\n'
        'kP<#M7:J=?k==Q<li[7Tp5)5BN=uL8\\rYuHQD@X<9lA17j)8Ss\n'
        'M/AnU`:AkrI3pb2[pce8Y?7$;M8In@+4Kd!b3Q%`e2;("+6&^p\n'
        'WsC+!n_q1>,G2+VUjLeb)"1lR`<S@R=XN`^+C3"ablSqh"u6Bu\n'
        "G(_i+.*f&)BeXtS0CEEH'AXZ2RS^iTQ?-\n"
        'n)f>Jm3O\'qWDLNoU"?[]a<PV-bfoN4<p=sON3UUb/#@5)d0Rua\n'
        'YdFWIclm9i3VA2+>lbAl1i=jYR3AqUS`J]Iun$bBa]D#',
    43: 'GarW7cYM8h\'ZUSufFN;_U";5f6^ebANpS+b-\n'
        '&$IlUWjWtClD5CCb)bP7l((K3j?H?Y.dX-Ij`oim&YQN[\\WZjk\n'
        '<45Z57[ZTlg7\\,-\n'
        "kFlg:3l[!'!KCsa8@k\\rlMqH6+JW]r)QL'+JM-\n"
        '\\KjXpu3+AY]Vu<`nNIE\\B*C:nTL#<Y#/U%o&rjO0^Tdj,:4+tr\n'
        '>ZN-\n'
        "e8)Uak[+qtOnNlkC]gOFRKUTTS+!g:ZD%H4]='TEYQJq>VJBX:\n"
        '=jlk#7&+?3GS/j\\nMV,C#3ZmE*83@_Z$UrpqCB;gb=$IEr%rN-\n'
        "T$$!RJb+ZF.dj8\\l#T1SipYU/r';WMR_LQ2:!%uh)d.1:r12?[\n"
        "!=MBFJiWcL!\\Ht_l/03^HlqJ[[ZUI'u-\n"
        '^6)A(/%&<8:@j"E]l]c4&#-"tq0&ZQY*j9-\n'
        'p52:,.)249]hLXObh_j/%9jM8(lKLE6Foct_fG6#"eWVZQj"&[\n'
        'S9b3-\n'
        ";N5%T?domsI!eZ&OpEV&#CGR[S?,l!H*pn3?:\\c'L+_.A?)>g5\n"
        "'Xq,GjR%?cQ=V1Hj>elq_'`*;d:`WH&>/`Z0i\\\\R=>$CG4,++I\n"
        '@0Ut16RmQNI:P=aGkptM;nlc>\\o,*4-\n'
        '&Wsj%i>r=AXKXk#U^2D/C6Z59*:JM5-\n'
        '48j!bn5;EGU1+/0;ra\\S6f3LnnK!B+WLM,Y9%idZp8A!dApY5n\n'
        'o4VmfPm,^[CZ8XDsE7=8V+<qgcIT*,f)P?sXo=k,Dd\\NqC`o"S\n'
        "As/Ngu48n)h8F2f*tY:@Zi?%#[fF]'m2@IV,4_f$p(S,;Luqig\n"
        'CJ/[a+70aOZ2ZqSY3rlsjO7N,>/+m4[P(9Ig',
    44: 'GarW7a_oie&;C;:6$p[9f)_+g$Tj@a0<p$q#.ar:A"Z)6/I^(%\n'
        '@_o>qBSkt@JbIAnfa$`1QD?Dskua`N\'`%^BLZ4BOmm"K!\'n+Zf\n'
        "UGV0#oc;bM'h\\9Trq7`>cMQsnGeq.O`%t@h8e$'FY%oYd:^&^E\n"
        ";k_GPNAgtpa,lYO(A/S5oq(GmMU9=:IK'R6iM%YI7FBmoR]9df\n"
        ':oa)_L(f6_=sJCCkr/a?r>3W]YIH/M2b3Oo8ll`n$4EIu8CYZH\n'
        '\\BbK]KMa>N4B./40Ns(+98g<n]EI=qc#)`2V(IZl2+"@mee2@5\n'
        '.m^du$VA\\l<\\>]W$`FDj(#n@6N,$-\n'
        '#:ZQdA*ZBY(4Xbnia@G9%eGCp25Ii[u6#[bEe0C`sW%p.Y:UG7\n'
        '&:d*FEC>\'N&XWkQ,]l(:@s1o"\'V<`rUI-IobA!NUMR$mD1+-\n'
        "&o!]/Vg\\.bgU5b+(_Mb':6==Uo#3LHY`'3Q)uR>MN8WOhH#_:F\n"
        "(P^Qu>dQq24O&m.__0_G*S\\i][j8<W8@E7oUI6q';#7s#u/_o1\n"
        '9-\n'
        "T!f&HN.bT6<([ss&^e(eb*BE7,cK:bAI0r9'*Dkl/!QC>W6Pr7\n"
        ',D@hM98pj0=JL\\+!kn,:\'?M<%)=#\'I[V+6J"`7_]c>Zo@;D;*G\n'
        "^QrDVA?$d!P=.CjuKns4DfEq%`5+)P;Ys11L.@LjlRQ)/]`,a'\n"
        "27R!E4f+nkYj(fU[-I0j-r>>n]?LZ?L(iM'Z",
    45: 'GatUo95E9I&:akBBb.c;3^Gqh:$UB:Cr_.GL=1`a)Zhn].>3tn\n'
        'Z:&6Fk`Ms_L%_ZR\\%eqmWj<63!PW\\WZeEId2m]j&5EGjB4[,%W\n'
        '.$#0TRITkH4^$,\\=n:JJr"oCL)s\'/Oi(quB)ZM0)#p9B:#W?E.\n'
        'D;,76J4TcR0PFj2?q7/qA4$o7"G$jbX&RNP=U2c\'Q\\76I_U&j[\n'
        'U+"?>@*&#@;CVuHRPBfW&E!c"-\n'
        "fnCt6FtqZ1Y1RmN\\Xo6#WlM2>t'jEQ%-\n"
        'TjEGDU"gQ[*fK9%bl%!%h/^!]_hMQea<Jhg3\'#g-\n'
        "?5Np6%pn;Npm:K$8^+#T`u&aER%':Am0ZTh1:&UBDZdt&?Z18@\n"
        '+^8B4O9lL`9G5!\\lIE$8/*"&.Pi_g\'Z6UEWYb^:@$CeU9D"3b!\n'
        '(5ntZu\\im=g)AW8iC2!3h,=^.lV8`>p0G8e$6JjQ%o*`2@DQp_\n'
        'M5<uOBabFo4k@Q0r/4:q8K$t_em!PUJ-\n'
        '?abp1*5Yf1:+:lC8b3@-\n'
        'dZjgXBeIDh@NGN+.cB<FhiD[*M_74fUarLhK;8!Z8f((1qVqCG\n'
        ')q$_G)Z.W5RqL8-\n'
        'a6,+%:V7[n.QR_l$0+Z\\,m=G4Pu`>S$l6M:/_8ZKZQ(Ql@M(QX\n'
        '/t<_,"UmOCng5`P1Tluj1UR$QQ7I`dKU8U=c;hJtA[]h>-\n'
        '+%uAa0\\PK*i?RioiljBgEM;1IW+/4eETrc[b?2B41I1CCXAipo\n'
        'VlX!45P,7o1\\&<*cZ00^V8m#4Qjt=6qorW',
    46: 'GasbW95i9E&:f[P"c(r]S^s\'0:m="tPK(<^\'e4\'c#8-\n'
        'S8BPieLX3TGi\\r@qc"F#b3b:he7Z4B#gT4/LOAnG\\iR9B"Xf_k\n'
        '>bCI?3PYrO$8j2J&T1;a\\qpi$/o-\n'
        'i_I&MjIn*IhkWeeg39G2/=<N",:SD,F>-\n'
        "+GVA(P'84(XmLdIe;ENV3p'dW%b2r(8!M1XR&muPf(XAR#o_q[\n"
        'fNtRsoBW_[%ECDioih`P#g3K84AA:6`1=;1R1/uh$Jfc:DYKGp\n'
        'P(@a%4]oo(TJaVeE+W!GT.asU$^5gL86S@Y#e48#jJ5Rl6-\n'
        'abBlb[:FI.d.@.GG&H)d\\n,S72(WF."^a1\\O4I22-\n'
        'MAl1]8t8>q00+1%,^?mcDDf$-\n'
        "%&'Z.R467S*?J=)9Iq[XI0O]aL:*Z%(efoEqmL$l%ld/J;S*#N\n"
        '/(VGKh+p`Y"L@&F\'@W1JlXT5O6)7O0a\'o`*829lL=%-\n'
        'Yqs7"S1[Qh+S8!rf`_iE&\\DN&M\\RmJ>4TWn(DO/haFGFF=;*a\\\n'
        'K#/i,]o_)[b&C.",TYLHd*:\'c0tFB[Q)=g8-7K:"L-\n'
        "E*Td4H?.+4PgP80YK9(Shqj]W%FT,7G_diu'E-\n"
        'RpB@u)Lo9He#d#SSP;Z[-\n'
        '^2[:a[_/dLGAtE3/Z)+J4O\\i67QdHZ@j;TOsERr;5OgN=!XS!=\n'
        "OB]tOH;.2S^,,h.b!('cGY[4EBMjn;WWMMb/>aWoe(ouS?^A%\\\n"
        'Ut^;[QL7-,[%W&-\n'
        "+qkb>=X\\(;:B?)C1)4T<mtbd0H'DT:XJ^E`,;!/n!c5(md[PtG\n"
        '?YO.%m8UTN\\0m?ddC9cRVg5<.qmSRZau-\n'
        '>UM\\_eTYWEjrs.s,JN<',
    47: 'Gas2Hhf%4&&BCiRh=f498UWbDdXVY#&4.e--H]Ng6PPpAC17]P\n'
        'jTO%#"=Hf8$(<2Xg2#Q2rP,\\0"@C`57*^X;q:t_i0gBj]]R.%2\n'
        'XW6fTYob=_lZ509"7.DMPKM54HW#l2nqH-\n'
        'T^ZiNuB#pUW2MTX\'64l0@\\E@Am*s.=WKRT&f_\'(PqK]i_/"Rc`\n'
        'o7E"O1!m385"f\',Ti(agtDC@Ar585uJ/])M)$Pb"J>XO`Z;8Z*\n'
        '(0m"OAQaGSjoY&:$gJnL\\.VMTaGM+J*l&fXTGDgI,\'1?qt\'1Co\n'
        '+S>n8NZVOH``3:T0Jl%S[14jWA"irHmYZHPf9*sFe-\n'
        "%^*R_i1[S2$'EDQ=UjF8FF)tk601,:.R<UXVYidU89PRZRs&FK\n"
        "IAddm>?W*=#qK1,i4II>XFX'-\n"
        'f/((GP_b(rcLe8i(XuQ6gp`C\\Mo2Xkdh"#UQb\\:!agaj"_Kh>p\n'
        't2$dNC1L#3uZ!"/.X1Z,Sj^>KSP[)i.(gDi<kqWcJ3WcS5<5iF\n'
        '2;6U@,fQH",>VL@+4.Wbf3>U,j33OHGJQ"=6+qBTX>DZ-\n'
        'U&B/\\JM>ne#?h;S9%9"hB9HAo2F!8%E+GiocJqFZ3lo\\]#54`!\n'
        'Xmm5JVCY=)3Jt%GU>krG]XCta3+bpk!:ubVrdhU9!^W@c"c2\\b\n'
        '7%4)8l-"GB1B`F/0/=e8l-\n'
        'GtF[<*Jd]uLn5_U+M4WYC>,tjZPOKWe^Vt*E1>L?M$KTDK9J_c\n'
        "K6I0'l\\cR1Q&V+iA>]ER2E#Em\\1-\n"
        "=HBYU;2k'IXC$MB#$Q<>LVK@:[6$5n>qXi8V,(L;i+)!/`s4OU\n"
        'U%_q/)^ig)C8rF#mnlUMg58f-\n'
        'To6Eb/=<Uie(FpYhh?=CT:]pRVjr]6e1,D+Gl-uQJOAkgbdd\\B\n'
        'W@7sgXPO`52!*>]%U%$3[P<;::+VMg2=;GVQ"?$7+LR+]kM1No\n'
        'h!"5jY+6nV?d',
    48: "Gasam95E9I&.ZXP4li4#^g>Ge'NGZJf#8,q9o<^bW%U.6Z^04/\n"
        "Ye1U7*3TEpp9%W/J$?\\`qiG>s\\'RDkc1@EqDcqMWr;,50;fZ/e\n"
        '2E8s+q<AH.a;CiQ-\n'
        '\\(`?^[UR[>Qjhs:^58^L?.)*CK0OM5=3f#9Mi/sq%847<=%gW#\n'
        'cPmTFm]Qfhn2\\r(t6K.f0]7."HguOp8%69[rOkRB%7Sh,HQs\'Q\n'
        'na9@!J)/DSjEU!<L8"TNUTtM;_$M%#0d-\n'
        "A&1TL/'GC<LTfiRC/uH_<#]-\n"
        '0T6Oa)r#k^45MY64a+LaL5R6Jj_6[<&FW#G.BU$5o[nP,4,-\n'
        'Bh#TJ.U-\n'
        'V7hofgbr\\"kXV_iu&Pt(P\'RiJqFnY%7,go]#W2fk_cm7.&3gM[\n'
        'U`bcX$oToLkJWpse()+h\\KCYb`g?!3Y^.^lqPjBPgJoq8Cb6Z?\n'
        ';*6/6D].J_!N&"LlgBJ87\'>T^tStBMe>R!;944m&C$mC\'D+QA:\n'
        '^Z:#sr1:iM08lS*^?\')/sY"100\\`gP^BU"2T^Df61C6u-\n'
        '=O=(Znj72W?]Gcu.Z7S6mQVe<N%=P+sA=Td-qS%mfJ@$ACq(Re\n'
        "+?ZaCf'''C'r!6h7V%U@l3E[\\5!bmT$Yos4HE[($a#o$kGCRXT\n"
        "u+%APp.$,$P)'!;\\d<U!d$2T2$@ZIpbQWL&4oA73d9WS%#bcYk\n"
        "g^?*/^0e\\<Jj]Q3Q_,ariG0b36.h'%&p,oOn^r.F<Zb(2R_88)\n"
        'NcZPP)eT2^Kd;rU6,<aN73B-p;Ec!n9',
    49: "GasJOcYq8d'ZVTK#nFT9K_2'ZBIhfE8bsqB>(g9N>m4\\fK$Z>7\n"
        "c:\\hYM5qtUoRI'gh_9Nhru?41/882D-\n"
        '$GgQim7MUH2_.Iot,C3=e4/2ZAJg8GYUSqOd5\\j)F)/!;<JI#5\n'
        "[;LK=A(rK<j?bm[!L:^A7.&;58FErl;#0Y*c'MC-\n"
        '6K4u[&kis4+u#hJo08B<t6g\'gd"X0/DKds@?Jm.Aq\\8Y;@0iP6\n'
        '?CoT$-\n'
        'bee,&"TgnsRr(MfN5[<eTdcX2oH>93JhZI8)4L\'P!P0&t\\P\'<(\n'
        'O?rDZJ*eX]D-\n'
        "(;=<M>=G=.M:na^kbeIA=S>L0Xc'$F95gV!61ac7uD^F6>S$-\n"
        'kLPq7]LO=J-\n'
        'B8[b0n<^,!FDUe)Vl/*tj;Mj,BbW=si&H6I)_Z]&@l-\n'
        '0hc0cflG9g1VKFnjuI(*^!$a#*usJnp=/+IY[U,)P(6Ht)5.O$\n'
        'C4o0=V.+,lAm93l@&]2_R<ITE.O(lc<SBGTI[a;4^_ZVU"5k6=\n'
        'MPA`,6_bF<P)N"d+3/#V2)5E^18)@hQ[KIcEsJYeZ7Bbs-\n'
        'Z5PnX:aKh`2A,[_3<&*u7DJ4N)Hefe25P0l],+^&35TKZj?!iC\n'
        'Vtb7/jl".CB5C71tO0Qs<NIe$epGX5@LLTH?jV]Fg!CRjW0^&J\n'
        'd-IETthh1W6n_\'`20LkC^Z:"mG2@+63b,M2:mI:@BI6/qMGlLc\n'
        '-8d+*J&l4".gLOGLeA(W$/gI76\\p)ho.4:h',
    50: 'Gat$t;/ao;&=u9?GhDn"GW=cN%]1dog,+f-\n'
        "g'N`nPp.LIMNF=[9iO'NP&rYo8E8NEQm_kaNg$hc\\fl&gik+g<\n"
        'GB`T5II$X"erchiBW^bbQ/_Ts?BH+3b?si4Vu.]"igDih?PPBZ\n'
        'NtKfI\\)Q7.co"CP1$k*.HoTj&O)Y?RISGJjM#_p!)]\\\'$]N/GL\n'
        '788H.MSs7"KTu-\n'
        "7X]o\\FQHI@P&j<=JCC=10_YH*:^>5Q6,#!2@m$@d0n$7<ZJS@'\n"
        "Gp'>'3$dH(TH%IO1&>?0=_'epDEo9!#iT1,?nVd(SJM;iT[TpM\n"
        '?qEJWrUgq!IIU8^5j":n-\n'
        'ST%aU\\6FW<FXr,+rkmS@&AGpnrJ\'/cH;s88g0T7Y"S?&#Gjgb?\n'
        'U<UG-\n'
        "'$9B?[.BGBhTU[n)h]Z=k9IM^$jNR0[fHLJ7[O5*\\sPg]<!tR(\n"
        'L:j*_Pd;cEe/gA)&goK@MNdsqda/@nPhe_aSu%@P*`+`(KiAKE\n'
        'jUHo+hEZV[#ct7++NsgAVLs9:3<UTNB1g%g15.Q>e]%uI`X/^a\n'
        "cGO>c8rAt%YYI`TjcF'\\NYVa7:9u]_6]uOTD2[GKNd#`=cZ+Q5\n"
        "3&.Q,Y'&SWHhJ>E[VPQk?6;AWUmP7i&)5s&Ni]BUB0_:1-\n"
        "[7W9H_[:fZ[?Nb_u;olH'Vr%^/(`m=H5=alll&b[cb_*)LhdCo\n"
        'eCg'}

SHOWCASE = [
    'Gat$u9l&KK&.NJM.-\n'
    "+LOFj+/3@iTo!QDI4o6Ce<^&?'Ln2(Nr`M:e!]b#j62dehn4^%\n"
    'SpYojM\'j?\'c$PH?qC=G"/7_fCN@/g0&"sG!<qSb1X`9SeDJbpe\n'
    "QA;K7E%np/X0JZN.I2YrIcEPV@3p%!%AH'u$561J;OmT8k=q\\6\n"
    '5nj(.)_X)=F!V0F]q$.%l_)g+7o#4)Yr]=tL^/Km76AI*,36LN\n'
    ';DYIbBg&cLh.1OG@Co\'hi]+L!\\]lR\\c!sN=X#"bZs*_lt3LeGd\n'
    'I="b0RS29ILTLIP$7ikE3Br\'ntFTRJL<hE6uF0(+QjQ^D/44.M\n'
    'HP<+6jp(.M,WR`\\S7si?bPD3P&MLm.\\Tm.>YkD&YTd?03gjY_N\n'
    '[G"X[@%o5G3OZ$2F,2N6FkTo<\'21e0D=1"(+%*<E.8N_oO?++(\n'
    '9bf"Hm_(LW2hKLft@86ng\'Z.]m\\WldtXF_@luo@`$22E/tflNL\n'
    '0F.5P4DNZa8!7O$rVg.b]Ig52jSXgcK"I(7Bs$jFcdpN\\:`e%,\n'
    'B4(;nBLZ`2/U1V3f(gRKQ6RZ^-:YRu$VT*5FB6)`o_-\n'
    '`^L&>>%Q8P]A<JTn9<PLEf(12LMtgV\\LYt.,kXW-D\\Pe-\n'
    '[Qs,HWbTZ\\4B\\3I8^EY2=#2,>0Jlq)a:?efN[i^Fa435Rj)g.G\n'
    "W%M,-U?P:*BY'uW\\q58l`R`Q\\jq2P3!Gc[QEr",

    'Gat%_cYM8h\'ZUSS(lY&0l#")l9*.PiXi>7+8YC/ia9%(_2M.\'.\n'
    "\\Mc!^Y`i*/'Y:noe,J5rQL/5YES*4gH-\n"
    "]:TU\\C@SQenA3hH?r]mk)Y]'`@VoZD;QI'#2ETQZs8Jr^mC565\n"
    'gLse5Ul+nDr%##"()3r#"<k8H(N1c3NTk6NY`IX<T-\n'
    '_WDjm,FZr]pJ!.V4gm6l60cfZ2/D_bqoo`]rX51IT-KsX"hZ%g\n'
    '0Z@dn)/#h,TKMY$$CqJ:RK&7/fBW&*]pg"??f4/*b4Op[@Eu$5\n'
    "uGCf$6Ztn'<%BSq`,3g'4&=Q03f$G&D_M$%;lK7EA'57_h%dW9\n"
    '8.tShH+rEE,Nlka6]1/hbriMmA*oWn3)`7SK7D$Ti&l)(rhIlf\n'
    'uRYf^NpFC*ODZ]q#[NIdbOLGIOffT3,$]-\n'
    '\'2P]6@fMs;ab"Vo,s^R3J]?;u,gS;&K;et99.T9g("HiN0?<8K\n'
    'r\\pChhJ&9"lK0MA_Xne_WXGu:AWQ"CPAUJ!#3?NCK(bo5.>=bA\n'
    'XIU^Uj`If:pmE(a535RJ_1Ko)uaHtAeUEs\\`(@I.-,\\=X-\n'
    'm*KA8sNitqi8%*PMh,)/.FF7p1!KLhY9Pg+_*0/5KS()StOLR(\n'
    '6@TU9aa0lqC[6T3BHpnr+',

    'GatUoh.tb!&ASZHkY%Q"[rS-\n'
    ")FP04PWc;mna<5;qKKrsUDahaUgh'4G&3EjB%CUJo:&TRB0AFU\n"
    '[4md(PP>:ka46cCDpDET6N1>d^P--8`%^5)Zc0.e!QEPe[+7`C\n'
    'D:^23GPVI93[-\n'
    'S5]kK(=$ZX^?EY#X]lAmk#I\\SJAQVL>tj3.M,"&5W`7@WXqmqR\n'
    'lp9$>CTo"rVrNBb6$g*GI%0\\T"8Z+C]s\\;,NMe2meVGZ-\n'
    "B*kFSVY:6K?7Y%3UseSeG@XK,EU6^iuNnDR[WO!.Q6G.U'\\s!:\n"
    '&Nt^eO5^\\gm\\Fi25r;RisV"J_<@IV.[0`eFVrc_5qJa*H_?&:3\n'
    'lDS-\n'
    "5k[2gtl1USZm(9YtbSu'(3[qL[0^knAS/4[^0gaou?L!O`s8`5\n"
    'lW3pM*<9p<ljN-oX@j_g*GZgZ=^IU)/Q<uE<l/"K64h&(C]T7>\n'
    'R]`d6l\\tG6m_:4`:8d<bOtQrT$PkG/*cFE05&g@eQbLb61sGBM\n'
    'O.BjAE?/Z[)b)4J?PI(C+*e]9`*i5ZO/O_X)12T</P/rTDA9Kg\n'
    'cH&\'Jeu?Ba*n.M1F_2@N%mQ19Q;fpK7&oE=HJ5#B"=7^3(]kjc\n'
    "RpC[-CMo;0Zl#CPQkrgUtG8?l<c5JbMa+Efb'q",

    'Gatm7cYM8h(bIS<LD>"!odaLuOlG*#lSsXI_W\\uFJ\\foI.<;LH\n'
    'KuOF=dXF1jf"5hKrni-er1c9[YWd^;5/$-\n'
    'W:R:skoCl0ra5TX4An"VP[J*D>j@Cio+8u"<5NsE#97jl)EmFX\n'
    "pqR$I%l\\u3QRF+no&c`L,Q5[Rp`nEs-?VLS7VuQhX7t<C'BS`-\n"
    '725F7QP=Ug\\AtO#h8h_T4=KMX].C_nVCe3U&>,2;Io8n6%@-\n'
    'H8][+CW#13B;WTiqQS/f^k%YtHr;Zu%\\.8bhQJ4eo;7#M*b(]\\\n'
    '\\R;@_ESA:c2&kJUJbTllj!>Q;-\n'
    'aGWtDi"XCokrSd`7oj0g)BB?.Gu4SZ?<l;bJaJlH$g\\X/!kSu_\n'
    ';!Z2JgB%^-WjMB)3_@rVpXl#OMPS^Lf\\C0_PE^-\n'
    '\'o_O6XV9ReS\'JjK^3,F@R@1jD;Qc>YZVij#^DF^)*"/W4X_Js,\n'
    'm:Z;dJ]E)g9cGH[;s=`):8ki.i[GGf"kM++kZ5@@.6$pbC4^U*\n'
    '%FDoV8(OO7UJ\\a$TKPN$i$j)"8f-\n'
    "#id2Q6^daA,4h?!H'Eu[!DiVZ/pQICQ1k1X'9r1j",
]

PUBLIC = [
    'Gb!$BcV"=*\'ZZ3?%bY"KoYcYWkj%C2\\nHbckX&+TOI.&$da29>\n'
    "f@i@jFe;mes4a]FY,2b0d.d$sR5aRjh`6'kipT\\5fM#Eh+5sIL\n"
    'pgFhsW.E"K:#oX"ZcM_9THUn_U\'a+]#!i)<_9;`t@2EZ/@4Q>;\n'
    'Ge,qMlmBrKo/nZuMg3;oeX=s16>#USTP,QZ!-\n'
    'GoVfCTNhQg"Z^?8deGZliUlRGRS?<:IeJ_Ud-\'lX(2O:\\]-\n'
    '$C5I+s-\n'
    'bT8T3]23Y*8&bm+?aGK[)Wl.HOA8KY^Ol>E,4AQ"k2)^VGH.PO\n'
    '*q[;E*"l3fm+e;;.D;">j0O)3Y_N0:Dn7b:]*7`"#?O8gTm2`3\n'
    ";:^2;M,+-].g5)+d:0j_sm5LHMD;[n<9.ADU9V,a0eEG'-\n"
    '\'X"JSjKPFj0P#:Ia^WSrupDL^GH-\n'
    ',bKW5lNl`D%B^,UCQd+U8CiY2dUX)$dShEc&W.;@.9]Lrb7tb]\n'
    '\'htMOX(\\;2/n<*^XI:V+KU@W@>`o$dd_,"p',
    'Gat$u9l&KK&.NJM.-\n'
    "+LOFj+/3@iTo!QDI4o6Ce<^&?'Ln2(Nr`M:e!]b#j62dehn4^%\n"
    'SpYojM\'j?\'c$PH?qC=G"/7_fCN@/g0&"sG!<qSb1X`9SeDJbpe\n'
    "QA;K7E%np/X0JZN.I2YrIcEPV@3p%!%AH'u$561J;OmT8k=q\\6\n"
    '5nj(.)_X)=F!V0F]q$.%l_)g+7o#4)Yr]=tL^/Km76AI*,36LN\n'
    ';DYIbBg&cLh.1OG@Co\'hi]+L!\\]lR\\c!sN=X#"bZs*_lt3LeGd\n'
    'I="b0RS29ILTLIP$7ikE3Br\'ntFTRJL<hE6uF0(+QjQ^D/44.M\n'
    'HP<+6jp(.M,WR`\\S7si?bPD3P&MLm.\\Tm.>YkD&YTd?03gjY_N\n'
    '[G"X[@%o5G3OZ$2F,2N6FkTo<\'21e0D=1"(+%*<E.8N_oO?++(\n'
    '9bf"Hm_(LW2hKLft@86ng\'Z.]m\\WldtXF_@luo@`$22E/tflNL\n'
    '0F.5P4DNZa8!7O$rVg.b]Ig52jSXgcK"I(7Bs$jFcdpN\\:`e%,\n'
    'B4(;nBLZ`2/U1V3f(gRKQ6RZ^-:YRu$VT*5FB6)`o_-\n'
    '`^L&>>%Q8P]A<JTn9<PLEf(12LMtgV\\LYt.,kXW-D\\Pe-\n'
    '[Qs,HWbTZ\\4B\\3I8^EY2=#2,>0Jlq)a:?efN[i^Fa435Rj)g.G\n'
    "W%M,-U?P:*BY'uW\\q58l`R`Q\\jq2P3!Gc[QEr",
    "GatUo5u5?_&;<]kGk'(qbF6,;6#!s-\n"
    '/KBG^!&99adAnGFZBZb5#V@eO9_?%XfDfW#Mf\'su)IF"2gR3M/\n'
    "VTHQ<5'j%lX9pUTkr]OTYXbU-5j.-\n"
    "4SA'gr;;oKm+<I;RKk*'9-\n"
    'P"nkGAO"EQ\\e+j!<4BRe4+uI#6Om]!\'$S/MZEV[JE1Nj#"V%A[\n'
    '=d9(?Y,XE-\n'
    '81"u:pS!Ep#UJ!*<JcrG_Y/e.D(%H#)qYubSFCq+Fr)Fnq?lk6\n'
    '-K95*)chM]M.NY"IofEiB7dN/f=`1\'&bdl?oQc2$%!p75Ch^Gq\n'
    '4cd+#O<Ws>2$XCobKiL-L@-pd$0P-\n'
    "=pCSuKYfH25$Oie2Y+`<i^EFmH?'\\pEUqp[>[D^7(u7[;S[_IS\n"
    '$bST0e(J3dEF$o\\QlfZ3mVEFs"kst8h;liF;$;\'WaH%Ad].5pL\n'
    'gN5^b0.WiqP+&7]7MR@APE;Zq5^*=HgU_5`KIV_YNp>,97Wh%R\n'
    '_,SmWMG"D\\U$*hEFka8A`),c!eP+`\'\'OA-\n'
    "3%FrlH?%h4s'5'E#<W",
    'Gat%_cYM8h\'ZUSS(lY&0l#")l9*.PiXi>7+8YC/ia9%(_2M.\'.\n'
    "\\Mc!^Y`i*/'Y:noe,J5rQL/5YES*4gH-\n"
    "]:TU\\C@SQenA3hH?r]mk)Y]'`@VoZD;QI'#2ETQZs8Jr^mC565\n"
    'gLse5Ul+nDr%##"()3r#"<k8H(N1c3NTk6NY`IX<T-\n'
    '_WDjm,FZr]pJ!.V4gm6l60cfZ2/D_bqoo`]rX51IT-KsX"hZ%g\n'
    '0Z@dn)/#h,TKMY$$CqJ:RK&7/fBW&*]pg"??f4/*b4Op[@Eu$5\n'
    "uGCf$6Ztn'<%BSq`,3g'4&=Q03f$G&D_M$%;lK7EA'57_h%dW9\n"
    '8.tShH+rEE,Nlka6]1/hbriMmA*oWn3)`7SK7D$Ti&l)(rhIlf\n'
    'uRYf^NpFC*ODZ]q#[NIdbOLGIOffT3,$]-\n'
    '\'2P]6@fMs;ab"Vo,s^R3J]?;u,gS;&K;et99.T9g("HiN0?<8K\n'
    'r\\pChhJ&9"lK0MA_Xne_WXGu:AWQ"CPAUJ!#3?NCK(bo5.>=bA\n'
    'XIU^Uj`If:pmE(a535RJ_1Ko)uaHtAeUEs\\`(@I.-,\\=X-\n'
    'm*KA8sNitqi8%*PMh,)/.FF7p1!KLhY9Pg+_*0/5KS()StOLR(\n'
    '6@TU9aa0lqC[6T3BHpnr+',
    'GatUoh.tb!&ASZHkY%Q"[rS-\n'
    ")FP04PWc;mna<5;qKKrsUDahaUgh'4G&3EjB%CUJo:&TRB0AFU\n"
    '[4md(PP>:ka46cCDpDET6N1>d^P--8`%^5)Zc0.e!QEPe[+7`C\n'
    'D:^23GPVI93[-\n'
    'S5]kK(=$ZX^?EY#X]lAmk#I\\SJAQVL>tj3.M,"&5W`7@WXqmqR\n'
    'lp9$>CTo"rVrNBb6$g*GI%0\\T"8Z+C]s\\;,NMe2meVGZ-\n'
    "B*kFSVY:6K?7Y%3UseSeG@XK,EU6^iuNnDR[WO!.Q6G.U'\\s!:\n"
    '&Nt^eO5^\\gm\\Fi25r;RisV"J_<@IV.[0`eFVrc_5qJa*H_?&:3\n'
    'lDS-\n'
    "5k[2gtl1USZm(9YtbSu'(3[qL[0^knAS/4[^0gaou?L!O`s8`5\n"
    'lW3pM*<9p<ljN-oX@j_g*GZgZ=^IU)/Q<uE<l/"K64h&(C]T7>\n'
    'R]`d6l\\tG6m_:4`:8d<bOtQrT$PkG/*cFE05&g@eQbLb61sGBM\n'
    'O.BjAE?/Z[)b)4J?PI(C+*e]9`*i5ZO/O_X)12T</P/rTDA9Kg\n'
    'cH&\'Jeu?Ba*n.M1F_2@N%mQ19Q;fpK7&oE=HJ5#B"=7^3(]kjc\n'
    "RpC[-CMo;0Zl#CPQkrgUtG8?l<c5JbMa+Efb'q",
    'Gatm7cYM8h(bIS<LD>"!odaLuOlG*#lSsXI_W\\uFJ\\foI.<;LH\n'
    'KuOF=dXF1jf"5hKrni-er1c9[YWd^;5/$-\n'
    'W:R:skoCl0ra5TX4An"VP[J*D>j@Cio+8u"<5NsE#97jl)EmFX\n'
    "pqR$I%l\\u3QRF+no&c`L,Q5[Rp`nEs-?VLS7VuQhX7t<C'BS`-\n"
    '725F7QP=Ug\\AtO#h8h_T4=KMX].C_nVCe3U&>,2;Io8n6%@-\n'
    'H8][+CW#13B;WTiqQS/f^k%YtHr;Zu%\\.8bhQJ4eo;7#M*b(]\\\n'
    '\\R;@_ESA:c2&kJUJbTllj!>Q;-\n'
    'aGWtDi"XCokrSd`7oj0g)BB?.Gu4SZ?<l;bJaJlH$g\\X/!kSu_\n'
    ';!Z2JgB%^-WjMB)3_@rVpXl#OMPS^Lf\\C0_PE^-\n'
    '\'o_O6XV9ReS\'JjK^3,F@R@1jD;Qc>YZVij#^DF^)*"/W4X_Js,\n'
    'm:Z;dJ]E)g9cGH[;s=`):8ki.i[GGf"kM++kZ5@@.6$pbC4^U*\n'
    '%FDoV8(OO7UJ\\a$TKPN$i$j)"8f-\n'
    "#id2Q6^daA,4h?!H'Eu[!DiVZ/pQICQ1k1X'9r1j",
    r"""
    Gat=gcV)/0'ZUFg#+h)c"1`6R+)0<`#k"EB7R7UU1aHp:2r*+q
   Wf%*Jn$s>9?aFY9lIa,K$a1h(htMCLJUE]s:WoS.2,Ts,.?gKH
   9d\@7;u%a*TCQ9F,P>CRA5-
   <ZS`5@2]?;Gn&JeC>IhNmsb])ET*^kMrU73%ZT4[#r#[i:Hp!5
   GK#\SE/jI<\b)=VAK!>`BQ69[]l+0Ku1"Qe^7X':41dk&2uF21
   ,+(#]qP/"mTCLV(3EG?r#IYnUH_6Abc$ic(FkCU6WP\6YSWU;5
   'uTnM-
   ."Nl,>\0$kJcnV;'7Mt=ip+i0cN.rHL5cc"@8;ADo`q5OV>I&`
   &N]#V>%F_U',_m[Cp#mZHI_1Q5;)"_ag5D`E@ui0jK]U='2iu8
   PQUKpfIYs=l/4C:rg7$R3#b)9R1fnm+blB\o'OB1]+[LZn+`(P
   ^gHNU/[u_X+L_<oJeZ+6.1/+_&KVAI#ToVnuE2$/V7L.+9[XJ4
   &T&N`""",
]

# --- RANGES ---
GLOBAL_RANGE = range(min(GLOBAL_STRS), max(GLOBAL_STRS) + 1)
MAIN_RANGE = range(1, 21)

PACK_RANGE = range(21, max(GLOBAL_STRS) + 1)

PACKS = {
    range(PACK_RANGE.start, 26): "Hidden Blocks",
    range(26, 31): "Countdown Blocks",
    range(31, 36): "Gravity Blocks",
    range(36, 41): "Teleporters",
    range(41, 46): "Launchers",
    range(46, PACK_RANGE.stop): "More Locks"
}

# --- CLASSES ---

class Coordinates(ABC):

    @property
    @abstractmethod
    def x(self):
        ...

    @property
    @abstractmethod
    def y(self):
        ...

    def __add__[_C](self: _C, other: Coordinates) -> _C:

        if not isinstance(other, Coordinates):
            return NotImplemented

        return type(self)(x=(self.x + other.x), y=(self.y + other.y))

    def __sub__[_C](self: _C, other: Coordinates) -> _C:

        if not isinstance(other, Coordinates):
            return NotImplemented

        return type(self)(x=(self.x - other.x), y=(self.y - other.y))

    def __mod__[_C](self: _C, mod: Coordinates) -> _C:

        if not isinstance(mod, Coordinates):
            return NotImplemented

        return type(self)(x=(self.x % mod.x), y=(self.y % mod.y))

    def __abs__[_C](self: _C) -> _C:

        return type(self)(x=abs(self.x), y=abs(self.y))

    def __mul__[_C](self: _C, i: int | float | _C) -> _C:

        if isinstance(i, Coordinates):
            return type(self)(x=(self.x * i.x), y=(self.y * i.y))
        else:
            return type(self)(x=(self.x * i), y=(self.y * i))

    def __rmul__[_C](self: _C, i: int | float) -> _C:

        if isinstance(i, Coordinates):
            return type(self)(x=(self.x * i.x), y=(self.y * i.y))
        else:
            return type(self)(x=(self.x * i), y=(self.y * i))


    def copy(self):
        return type(self)(self.x, self.y)

    def __iter__(self):
        return iter([self.x, self.y])

    def __complex__(self):

        return complex(self.x, self.y)

    def adj[_C](self: _C, direction: str, g: Literal[1, -1]=1) -> _C:

        _C = type(self)

        x, y = self

        match direction:

            case "w":
                return _C(x, y+g)
            case "a":
                return _C(x-1, y)
            case "s":
                return _C(x, y-g)
            case "d":
                return _C(x+1, y)
            case "as" | "sa":
                return _C(x-1, y-g)
            case "sd" | "ds":
                return _C(x+1, y-g)
            case "wd" | "dw":
                return _C(x+1, y+g)
            case "aw" | "wa":
                return _C(x-1, y+g)
            case "ww":
                return _C(x, y+2*g)
            case "ss":
                return _C(x, y-2*g)

    def adjs[_C](self: _C, *directions: str, g: Literal[1, -1]=1) -> set[_C]:

        return {self.adj(d, g).as_frozen() for d in directions}

    @classmethod
    def arc[_C1, _C2, _C3](cls, endpoint_1: _C1, endpoint_2: _C2,
                           invert=False) -> Generator[_C3, None, None]:

        if not (isinstance(endpoint_1, Coordinates)
                and isinstance(endpoint_2, Coordinates)):
            raise ValueError("Expected 'Coordinate' type.")

        if invert:
            endpoint_1, endpoint_2 = endpoint_2, endpoint_1

        x1, x2 = endpoint_1.x, endpoint_2.x
        y1, y2 = endpoint_1.y, endpoint_2.y

        # Go in the vertical direction
        a = 1 if y1 <= y2 else -1
        for y in range(y1, y2 + a, a):
            yield cls(x1, y)

        # Go in the horizontal direction
        a = 1 if x1 <= x2 else -1
        for x in range(x1, x2 + a, a):
            yield cls(x, y2)

    @classmethod
    def box[_C1, _C2, _C3](cls, endpoint_1: _C1, endpoint_2: _C2
                           ) -> Generator[_C3, None, None]:

        for invert in (True, False):
            yield from cls.arc(endpoint_1, endpoint_2, invert=invert)

    # The next two/three methods are HEAVILY documented.
    # Just the nature of Bresenham's algorithms.

    @classmethod
    def line[_C1, _C2, _C3](cls, endpoint_1: _C1, endpoint_2: _C2
                            ) -> Generator[_C3, None, None]:

        # Bresenham's algorithm for lines
        # (Don't know completely how it works lol, it just does)

        x0, y0 = endpoint_1
        x1, y1 = endpoint_2

        # Displacement
        dx, dy = endpoint_2 - endpoint_1

        # Decompose displacements into sign and distance
        sx, dx = 1 if dx > 0 else -1, abs(dx)
        sy, dy = 1 if dy > 0 else -1, abs(dy)

        # Prioritize horizontal over vertical.
        M, m = C(sx, 0), C(0, sy)
        major, minor = dx, dy

        # Prioritize vertical over horizontal for steep lines.
        if dy > dx:
            M, m = m, M
            major, minor = minor, major

        # Error term. Decides when to go in the minor direction.
        D = 2*minor - major

        current = endpoint_1.as_normal()

        for _ in range(major + 1):

            yield current

            # When error gets too large, go in the minor direction.
            # Then push the error down.
            if D >= 0:
                current += m
                D -= 2*major

            # Build up the error for going in the major direction.
            current += M
            D += 2*minor

    @classmethod
    def _octants(cls, center, x, y) -> Generator[FrozenC]:

        c1, c2 = C(x, y), C(y, x)

        # c2 completes the arc from the other side
        # of the quadrant. It is reflected over y = x.

        # Rotate directions of c1 and c2.
        for mul in C(1, 1), C(1, -1), C(-1, 1), C(-1, -1):

            # add directed (x, y) to center
            # to readjust to radius.
            yield center + mul*c1
            yield center + mul*c2

    @classmethod
    def circle[_C1, _C3](cls, center: _C1, radius: int
                         ) -> Generator[_C3, None, None]:

        x0, y0 = center

        # Error variable: tracks how far outside (x, y) is.
        f = 1 - radius

        # Slope of the circle (derivative). How much to change the error
        # given a movement in x or y; how much x or y is pushed outside.
        fx, fy = 1, 2 * radius

        # Coordinates
        x, y = 0, radius

        # Root coordinates
        for offset in C(0, radius), C(0, -radius), C(radius, 0), C(-radius, 0):
            yield center + offset

        # Note that (x, y) sweeps out an arc from 90 degrees to 45 degrees.
        # x is smaller than y until x = y = about sqrt(2)/2.
        # Then, octants are drawn.
        while x < y:

            # ERROR IS TOO LARGE.
            if f >= 0:

                y -= 1 # Pull y closer to circle.
                fy -= 2 # Decrease the correction factor.
                f -= fy # Subtract error.

            x += 1 # Move x forward, pulls x farther from circle.
            fx += 2 # Increase correction factor.
            f += fx # Increase error.

            # x and y are reflected to complete all 7 other arcs as well
            # as the normal 90-45 arc.
            yield from cls._octants(center, x, y)

    def __str__(self):

        return f"<{self.x} {self.y}>"

@dataclass(slots=True)
class C(Coordinates):

    x: int = 5
    y: int = 3

    def __post_init__(self):
        if not (isinstance(self.x, int) and isinstance(self.y, int)):
            raise ValueError("Coordinates are not integers.")

    def __iadd__[_C](self: _C, other: Coordinates) -> _C:

        if not isinstance(other, Coordinates):
            return NotImplemented

        self.x, self.y = (self.x + other.x), (self.y + other.y)
        return self

    def __isub__[_C](self: _C, other: Coordinates) -> _C:

        if not isinstance(other, Coordinates):
            return NotImplemented

        self.x, self.y = (self.x - other.x), (self.y - other.y)
        return self

    def __imod__[_C](self: _C, mod: Coordinates) -> _C:

        if not isinstance(mod, Coordinates):
            return NotImplemented

        self.x, self.y = (self.x % mod.x), (self.y % mod.y)
        return self

    def as_frozen(self) -> FrozenC:
        return FrozenC(self.x, self.y)

    def as_normal(self) -> C:
        return self

@dataclass(slots=True, frozen=True)
class FrozenC(Coordinates):

    x: int = 5
    y: int = 3

    def __post_init__(self):
        if not (isinstance(self.x, int) and isinstance(self.y, int)):
            raise ValueError("Coordinates are not integers.")

    def as_frozen(self) -> FrozenC:
        return self

    def as_normal(self) -> C:
        return C(self.x, self.y)

class Map(ABC):

    # defined.
    def __init__(self, _map: list[str] | Map=None) -> None:

        if _map is None:
            _map = [" "*63 for i in range(9)] \
                   + ["#"*63 for i in range(3)]

        if isinstance(_map, Map):
            self.map = _map.map.copy()
        elif isinstance(_map, list):

            if not Map._valid_list(_map):
                raise ValueError("Not a valid list.")

            self.map = _map.copy()
        else:
            raise ValueError(f"{_map} is not list or Map.")

    @staticmethod
    def _valid_list(_map: list):

        if not _map:
            return False
        if not all(isinstance(line, str) for line in _map):
            return False

        # All lines of the map must have uniform width
        if len({len(line) for line in _map}) > 1:
            return False

        return True

    @property
    def x_len(self):
        return len(self.map[0])
    @property
    def y_len(self):
        return len(self.map)

    @classmethod
    def solid(cls, char: str, length: int, width: int):

        if len(char) != 1:
            raise ValueError(f"Expected 1 character, got {char!r}")

        return cls([char*length for i in range(width)])

    def _bounded(self, key: Coordinates):

        x_in_bounds = 0 <= key.x < self.x_len
        y_in_bounds = 0 <= key.y < self.y_len

        return (x_in_bounds and y_in_bounds)

    def __eq__(self, other):

        if not isinstance(other, Map):
            return False

        return self.map == other.map

    def __getitem__(self, key: Coordinates | int | slice) -> str:

        if isinstance(key, Coordinates):

            if not self._bounded(key):
                return "%"

            x, y = key
            char = self.map[self._flip(y)][x]
            return char

        elif isinstance(key, int):

            return self.map[self._flip(key)]

        elif isinstance(key, slice):

            start = 0 if key.start is None else key.start
            stop = len(self.map) if key.stop is None else key.stop

            # Flip y-values
            stop = self.y_len-stop
            start = self.y_len-start

            return type(self)(self.map[stop:start])

        else:
            raise ValueError(f"{key!r} is not a valid key.")

    def enumerate(self) -> Iterator:

        for coord_tuple in product(range(self.x_len), range(self.y_len)):
            coord = C(*coord_tuple)

            yield coord, self[coord]

    def __iter__(self) -> Iterator:

        return iter(reversed(self.map))

    def copy(self):

        return type(self)(deepcopy(self.map))

    def __contains__(self, char) -> bool:
        return any([char in row for row in self.map])

    def __reversed__(self):
        return self.map

    def __len__(self):

        return self.y_len

    def count(self, substr: str):

        return sum(row.count(substr) for row in self.map)

    def _flip(self, y: int):

        return self.y_len - 1 - y

    def __format__(self, format_spec: str):

        n = len(format_spec)

        if n > 2:
            raise ValueError("Format specifier is longer than 2 characters")

        h = format_spec[0] if n > 0 else "~"
        v = format_spec[1] if n > 1 else "|"

        lst = []

        horizontal_border = f"{h*(self.x_len+2)}"

        lst.append(horizontal_border)

        for row in self.map:
            lst.append(f"{v}{''.join(row)}{v}")

        lst.append(horizontal_border)

        return "\n".join(lst) + "\n"

    def __str__(self):

        return format(self, "")

    @abstractmethod
    def __setitem__(self, key: Coordinates, val: str):
        ...

    def find(self, chars: Iterable[str], include_character=True):

        """Used during platform generation. It finds all
        of the occurrences in the game map of characters.
        """

        result = set()
        for y, row in enumerate(self):
            for x, char in enumerate(row):
                for i in chars:
                    if char == i:

                        result.add((FrozenC(x, y), char)
                                   if len(chars) > 1 and include_character
                                   else FrozenC(x, y))

        return result

    def reflected(self, dim: str="x"):

        if dim == "x":
            return type(self)(self.map[::-1])
        elif dim == "y":
            return type(self)([line[::-1] for line in self.map])
        else:
            raise ValueError(f"Expected 'x' or 'y', got {dim}")

    def replaced(self, old_char: str, new_char: str):

        new = self.copy()
        new.replace(old_char, new_char)
        return new

    def replace(self, old_char: str, new_char: str):

        if len(old_char) != 1 or len(new_char) != 1:
            raise ValueError("Character must have length 1.")

        coords = self.find(old_char)

        for coord in coords:
            self[coord] = new_char

class GameMap(Map):

    def __setitem__(self, key: Coordinates, val: str) -> None:

        if not isinstance(val, str):
            raise ValueError(f"Expected string, got {val!r}")
        elif len(val) != 1:
            raise ValueError(
                f"Expected one character, got {val!r} with length {len(val)}"
            )

        if not (isinstance(key, Coordinates) or isinstance(key, int)):
            raise ValueError(f"{key!r} is not a valid key.")

        if isinstance(key, int) and key in range(self.y_len):
            self.map[self._flip(key)] = [val for i in range(self.x_len)]

        elif self._bounded(key):

            x, y = key
            row = list(self.map[self._flip(y)])
            row[x] = val

            row = "".join(row)
            self.map[self._flip(y)] = row

@dataclass(slots=True)
class MultiMap:

    game_map: GameMap
    default_map: GameMap

    def patch(self, coord: Coordinates):

        char = self.default_map[coord]
        self.game_map[coord] = char

    def __setitem__(self, coord: Coordinates, char: str):

        self.game_map[coord] = char
        self.default_map[coord] = char

class Patch(ABC):

    @abstractmethod
    def apply(self, game_map: Map) -> None:
        ...

    @abstractmethod
    def get(self, game_map: Map) -> Patch:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[Coordinates]:
        ...

class BoxPatch(Patch):

    def __init__(self, coord_1: Coordinates, coord_2: Coordinates,
                 game_map: Map):

        x1, y1 = coord_1
        x2, y2 = coord_2

        self.coord_1 = C(min(x1, x2), min(y1, y2))
        self.coord_2 = C(max(x1, x2), max(y1, y2))

        # The only attributes required to calculate this
        # are the two previously defined ones.

        self.patch = self.__get_patch(game_map)

    def __iter__(self) -> Iterator[Coordinates]:

        p = product(range(self.coord_1.x, self.coord_2.x+1),
                    range(self.coord_1.y, self.coord_2.y+1))

        for coord in p:
            yield FrozenC(*coord)

    def __get_patch(self, game_map: Map) -> GameMap:

        return GameMap(
            [
                row[self.row_slice] for row in game_map[self.map_slice]
            ][::-1]
        )

    @property
    def row_slice(self):

        return slice(self.coord_1.x, self.coord_2.x+1, None)

    @property
    def map_slice(self):

        return slice(self.coord_1.y, self.coord_2.y+1, None)

    def apply(self, game_map: GameMap) -> None:

        for coord in self:

            # Normalize coordinate so it can index the patch.
            patch_coord = coord - self.coord_1

            game_map[coord] = self.patch[patch_coord]

    def get(self, game_map: Map) -> BoxPatch:

        return BoxPatch(self.coord_1, self.coord_2, game_map)

class OrganicPatch:

    def __init__(self, game_map: Map):

        self.patch_dict = dict()

        for coord, char in game_map.enumerate():

            if char != "%":
                self.patch_dict[coord.as_frozen()] = char

    def __iter__(self):

        return iter(self.patch_dict)

    def apply(self, game_map: GameMap) -> None:

        for coord, char in self.patch_dict.items():

            game_map[coord] = char

    def get(self, game_map: GameMap) -> OrganicPatch:

        length, width = game_map.x_len, game_map.y_len

        new_map = GameMap.solid("%", length, width)

        for coord in self.patch_dict:
            new_map[coord] = game_map[coord]

        return OrganicPatch(new_map)

class MemoryEfficientInfoMsgs:

    # no-access, doesn't contain maps.
    # suitable for save strings.

    def __init__(self, msgs: list[str] | MemoryEfficientInfoMsgs=None):

        if isinstance(msgs, MemoryEfficientInfoMsgs):
            self.msgs = msgs.msgs.copy()

        elif msgs is None:
            self.msgs = []
        else:
            self.msgs = msgs.copy()

    def __repr__(self):

        msgs = ", ".join(repr(msg) for msg in self.msgs)
        return f"MemoryEfficientInfoMsgs({msgs})"

    def copy(self):

        return MemoryEfficientInfoMsgs(deepcopy(self.msgs))

    def __eq__(self, other):

        if not isinstance(other, MemoryEfficientInfoMsgs):
            return False

        return self.msgs == other.msgs

    def __iter__(self):

        return iter(self.msgs)

class InfoMsgs(MemoryEfficientInfoMsgs):

    __slots__ = ("info_dict",)

    def __init__(self, info_dict: dict[Coordinates, str]):

        self.info_dict = info_dict

    @property
    def id(self):
        raise ValueError("Cannot get id")

    @classmethod
    def from_memory_efficient(cls, info_msgs: MemoryEfficientInfoMsgs,
                              game_map: GameMap):

        coords = []

        for y, row in enumerate(game_map):

            row_coords = []
            for x, char in enumerate(row):
                if char == "?":
                    row_coords.append(FrozenC(x, y))
            coords.extend(reversed(row_coords))

        return InfoMsgs(dict(zip(reversed(coords), info_msgs)))

    def __repr__(self):

        coord_list = ', '.join(f'{(coord.x, coord.y)}: {msg}'
                               for coord, msg in self.info_dict.items()
                               )
        return f"InfoMsgs({coord_list})"

    @property
    def coords(self):

        # Sort coords based on left to right, up to down order.
        return sorted(list(self.info_dict),
                      key=lambda coord: (-coord.y, coord.x))

    @property
    def msgs(self):

        return [self.info_dict[coord] for coord in self.coords]

    def items(self):
        return self.info_dict.items()

    def __getitem__(self, key: Coordinates):

        return self.get(key)

    def get(self, key: Coordinates, default_value: Any=""):

        return self.info_dict.get(key.as_frozen(), default_value)

    def __setitem__(self, key: Coordinates, msg: str):

        self.info_dict[key.as_frozen()] = msg

    def pop(self, key: Coordinates):

        self.info_dict.pop(key.as_frozen(), None)

    def __contains__(self, coord: Coordinates):

        return coord.as_frozen() in self.info_dict

    def copy(self):

        return InfoMsgs(deepcopy(self.info_dict))

@dataclass(slots=True)
class LevelData:

    map: Optional[GameMap] = field(default_factory=GameMap)
    msg: Optional[str] = ""
    time: Optional[int | float] = float("inf")
    title: Optional[str] = "Untitled"
    info: Optional[MemoryEfficientInfoMsgs] = field(
        default_factory=MemoryEfficientInfoMsgs)
    points: Optional[int] = 0
    author: Optional[str] = "Unknown"
    date: Optional[str] = field(
        default_factory=lambda: datetime.now().strftime(
            "%m/%d/%Y, %I:%M:%S %p"
        )
    )

    MAX_MSG_WIDTH: ClassVar[int] = 300
    MAX_INFO_WIDTH: ClassVar[int] = 200
    MAX_TITLE_WIDTH: ClassVar[int] = 100
    MAX_AUTHOR_WIDTH: ClassVar[int] = 25
    MAX_TIME: ClassVar[int] = 1_000

    def __post_init__(self):

        attrs = [
            self.map,
            self.msg,
            self.time,
            self.title,
            self.info,
            self.points,
            self.author
        ]

        if all(x is None for x in attrs):
            return

        if not isinstance(self.map, GameMap):
            raise ValueError("map is not a GameMap object")
        if not isinstance(self.msg, str):
            raise ValueError("msg is not a string")
        if not (isinstance(self.time, int) or isinstance(self.time, float)):
            raise ValueError("time is not an integer or float.")
        if self.time <= 0.0:
            raise ValueError("time is nonpositive.")
        if not isinstance(self.title, str):
            raise ValueError("title is not a string")
        if not isinstance(self.info, MemoryEfficientInfoMsgs):
            raise ValueError("info is not a MemoryEfficientInfoMsgs object")
        if not isinstance(self.points, int):
            raise ValueError("points is not an integer")
        elif self.points not in range(6):
            raise ValueError("points is not in range 0 to 5.")
        if not (self.author and isinstance(self.author, str)):
            raise ValueError("Received wrong value for author")

    @property
    def start(self):

        if self == LevelData.NULL:
            return C()
        elif not self:
            raise ValueError(f"Corrupted LevelData object {self}")

        for y, row in enumerate(self.map):
            for x, char in enumerate(row):
                if char == "S":
                    return C(x, y)

        return C()

    def text_len(self):
        raise DeprecationWarning("Use text_length instead.")

    def as_id(self) -> str:

        strs = (
            "None" if self.map is None else "".join(self.map.map),
            str(self.msg),
            str(self.time),
            str(self.title),
            str(self.info),
            str(self.points),
            str(self.author)
        )

        binary = [
            string.encode("utf-8").replace(b"\x00", b"")
            for string in strs
        ]

        bytes_obj = b"\x00".join(binary)

        return sha256(bytes_obj).hexdigest()

    def text_length(self, display_msg: bool):

        if self == LevelData.NULL:
            return -1
        elif not self:
            raise ValueError(f"Corrupted LevelData object {self}")

        new_title = shorten(self.title.upper(), width=(self.map.x_len // 3),
                            placeholder="..."
                            )

        formatted_msg = shorten(
            f"[{new_title!s}] {(self.msg if display_msg else '')!s}",
            width=self.map.x_len, placeholder="..."
        )

        txts = [
            formatted_msg,
            *self.info,
            "[||] PAUSED",
            "Launch!"
        ]

        txts = map(lambda txt: f"@ | {txt}", txts)

        lens = [
            len(wrap(txt.replace("\n", ""), width=self.map.x_len+2))
            for txt in txts
        ]

        return max(lens)

    def score(self, result: Result):

        return self.points * result.order

    def as_tuple(self):

        return (
            self.map,
            self.msg,
            self.time,
            self.title,
            self.info,
            self.points,
            self.author,
            self.date
        )

    def as_stuple(self):

        return (
            self.map,
            self.msg,
            self.time,
            self.title,
            self.info,
            self.points,
            self.author,
            self.date,
            self.as_id() # checksum
        )

    def copy(self):

        if self == LevelData.NULL:
            return LevelData.NULL
        elif not self:
            raise ValueError(f"Corrupted LevelData object {self}")

        map_, msg, time, title, info, points, author, date = self

        return LevelData(
            map_.copy(),
            msg,
            time,
            title,
            info.copy(),
            points,
            author,
            date
        )

    @classmethod
    def from_tuple(cls, args: tuple):

        return LevelData(*args)

    @classmethod
    def from_stuple(cls, args: tuple):
        data, checksum = args[:-1], args[-1]
        new = cls.from_tuple(data)
        if new.as_id() != checksum:
            raise ValueError(
                "Save string was manipulated; checksum does not match"
            )
        else:
            return new

    @classmethod
    def from_save_str(cls, save_str: str) -> LevelData:

        decoded = decompress(base64.a85decode(save_str.encode("utf-8")))

        return LevelData.from_stuple(pickle.loads(decoded))

    def as_save_str(self):

        if not self and self != LevelData.NULL:
            raise ValueError(f"Corrupted LevelData object {self}")

        encoded = compress(pickle.dumps(self.as_stuple()))

        save_str = base64.a85encode(encoded, wrapcol=0)
        return save_str.decode("utf-8")

    def as_dict(self):

        if not self and self != LevelData.NULL:
            raise ValueError(f"Corrupted LevelData object {self}")

        return asdict(self)

    def __bool__(self):

        return not any(attr is None for attr in self.as_tuple())

    def __eq__(self, other):

        if not isinstance(other, LevelData):
            return False

        return self.as_tuple() == other.as_tuple()

    def __iter__(self):

        if not self and self != LevelData.NULL:
            raise ValueError(f"Corrupted LevelData object {self}")

        return iter(self.as_tuple())

    def __repr__(self):

        return f"LevelData(title={self.title!r})"

LevelData.NULL = LevelData(
    None,
    None,
    None,
    None,
    None,
    None,
    None
)

class LevelDatabase:

    __slots__ = ("save_str_list",
                 "levels",
                 "ids",
                 "ids_to_records",
                 "ids_to_levels",
                 "ids_to_titles")

    def __init__(self, save_str_list: list[str]=None) -> None:

        if save_str_list is None:
            save_str_list = []

        self.save_str_list: list[str] = save_str_list

        # --- Cached Attributes ---

        self.levels = [LevelData.from_save_str(save_str)
                       for save_str in self.save_str_list]

        self.ids = {
            lvl.as_id(): lvl.as_save_str() for lvl, save_str
            in zip(self.levels, self.save_str_list)
        }

        self.ids_to_levels = {lvl.as_id(): lvl for lvl in self.levels}
        self.ids_to_titles = {lvl.as_id(): lvl.title for lvl in self.levels}

        self.ids_to_records = {lvl.as_id(): lvl.time for lvl in self.levels}

        # --- Cached Attributes <end> ---

    @classmethod
    def from_levels(cls, level_list: list['LevelData']):

        return cls([lvl.as_save_str() for lvl in level_list])

    @classmethod
    def from_range(cls, r: range):

        return cls([GLOBAL_STRS[i] for i in r])

    @property
    def times(self):

        return list(self.ids_to_records.values())

    @property
    def tuples(self):

        return [level_data.as_tuple() for level_data in self.levels]

    @property
    def titles_dict(self):

        return {i.title: i for i in self.levels}

    def query(self, search: str):

        titles = difflib.get_close_matches(search, list(self.titles_dict))
        matches = [self.titles_dict[title] for title in titles]

        return type(self).from_levels(matches)

    def copy(self):

        return type(self)(self.save_str_list)

    def __bool__(self):
        return bool(self.save_str_list)

    def __len__(self):
        return len(self.save_str_list)

    def __iter__(self):
        return iter(self.levels)

    def __repr__(self):

        return f"LevelDatabase({self.save_str_list})"

class IndexedDatabase(LevelDatabase):

    def __contains__(self, obj):

        if isinstance(obj, str):
            return obj in self.titles_dict

        else:
            return obj in self.levels

    def __getitem__(self, obj):

        if isinstance(obj, str):

            return self.titles_dict[obj]

        elif isinstance(obj, float):
            if isnan(obj):
                return LevelData.NULL
            else:
                raise IndexError(f"Received {obj}.")

        try:
            return self.levels[obj]
        except IndexError:
            raise IndexError(f"Received {obj}.")

# --- DATABASES ---

GLOBAL_DATABASE = IndexedDatabase.from_range(GLOBAL_RANGE)
SHOWCASE_DATABASE = IndexedDatabase(SHOWCASE)
PUBLIC_DATABASE = IndexedDatabase(PUBLIC)
