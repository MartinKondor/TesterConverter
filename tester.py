from re import sub as replace_pattern
from collections import OrderedDict


class TesterConversionError(Exception):
    pass


def int_from_txt(filename):
    ints = []

    with open(filename, 'r') as file:
        for line in file.read().splitlines():
            if line:
                try:
                    ints.append( abs(int(replace_pattern(r'[^\d]', '', line.strip()))) )
                except Exception:
                    raise TesterConversionError()
    try:
        # Az első nulla elötti értékek ignorálása (implicit)
        ints = ints[ints.index(0):]
    except Exception:
        raise TesterConversionError()

    return ints


def build_dict():
    a_ret = {}

    # 256 / 4
    n_base_c = 4
    n_base_a = 6
    index = 0
    for i in range(64):
        a_ret['A' + str(index + 1)] = n_base_a
        a_ret['A' + str(index + 2)] = n_base_a + 1
        a_ret['A' + str(index + 3)] = a_ret['A' + str(index + 2)] - 4
        a_ret['A' + str(index + 4)] = a_ret['A' + str(index + 3)] - 2
        a_ret['A' + str(index + 5)] = a_ret['A' + str(index + 4)] + 13
        n_base_a = a_ret['A' + str(index + 5)]	

        index += 4

    index = 0

    for i in range(64):
        a_ret['C' + str(index + 1)] = n_base_c
        a_ret['C' + str(index + 2)] = n_base_c + 1
        a_ret['C' + str(index + 3)] = a_ret['C' + str(index + 2)] - 5
        a_ret['C' + str(index + 4)] = a_ret['C' + str(index + 3)] + 2
        a_ret['C' + str(index + 5)] = a_ret['C' + str(index + 4)] + 10
        n_base_c = a_ret['C' + str(index + 5)]

        index += 4
    
    return OrderedDict(sorted({a_ret[k]: k for i, k in enumerate(a_ret)}.items()))


def create_pairs(numbers, nth=0):
    dictionary = build_dict()
    collector = {}
    
    for i, n in enumerate(numbers[2:]):
        if not n in collector.keys():
            collector[n] = []
		
        nn = i + (nth * 128)
        if n != nn:
            collector[n].append(nn)

    result = {}

    for k in collector.keys():
        l = [k] + collector[k]
        l = sorted(l, reverse=True)
        result[l[0]] = l[1:]

    return result

    dictionary = build_dict()
    collector = {}
    
    for i, n in enumerate(numbers[2:]):
        if not n in collector.keys():
            collector[n] = []
		
        if n != i:
            collector[n].append(i)

    return collector
	
    dictionary = build_dict(False)
    pairs = []
    pre_pair_a, pre_pair_b = '1', '1'

    for i, n in enumerate(numbers):
        pair_a = dictionary.get(n)
        if pair_a is None:
            continue

        pat_a = int(replace_pattern(r'\D', '', pair_a)) + (nth * 64)  # 64 | 128
        if 1 <= pat_a <= 32:
            pre_pair_a = '1'
        elif 33 <= pat_a <= 64:
            pre_pair_a = '2'
        elif 65 <= pat_a <= 96:
            pre_pair_a = '3'
        elif 97 <= pat_a <= 127:
            pre_pair_a = '4'
        elif 128 <= pat_a <= 159:
            pre_pair_a = '5'

        while pat_a > 32:
            pat_a -= 32

        pair_b = dictionary.get(i)
        if pair_b is None:
            continue

        pat_b = int(replace_pattern(r'\D', '', pair_b)) + (nth * 64)
        if 1 <= pat_b <= 32:
            pre_pair_b = '1'
        elif 33 <= pat_b <= 64:
            pre_pair_b = '2'
        elif 65 <= pat_b <= 96:
            pre_pair_b = '3'
        elif 97 <= pat_b <= 127:
            pre_pair_b = '4'
        elif 128 <= pat_b <= 159:
            pre_pair_b = '5'

        while pat_b > 32:
            pat_b -= 32

        pairs.append([pre_pair_b,
                      replace_pattern(r'\d', '', pair_b) + str(pat_b),
                      pre_pair_a,
                      replace_pattern(r'\d', '', pair_a) + str(pat_a)])
    
    return pairs


def int_to_adaptronic(numbers, nth=0):
    """
    :param numbers: list of numbers
    :return: Converted list of numbers
    """
    return
    raw_pairs = create_pairs(numbers, nth)
    pairs = []

    for pair in raw_pairs:
        p = pair
        if p[0] == '1':
            p[0] = '2'
        elif p[0] == '2':
            p[0] = '1'
        elif p[0] == '3':
            p[0] = '4'
        elif p[0] == '4':
            p[0] = '3'

        if p[2] == '1':
            p[2] = '2'
        elif p[2] == '2':
            p[2] = '1'
        elif p[2] == '3':
            p[2] = '4'
        elif p[2] == '4':
            p[2] = '3'

        if 'C' in p[1]:
            p[1] = p[1].replace('C', 'A')
        elif 'A' in p[1]:
            p[1] = p[1].replace('A', 'C')

        if 'C' in p[3]:
            p[3] = p[3].replace('C', 'A')
        elif 'A' in p[3]:
            p[3] = p[3].replace('A', 'C')

        pairs.append(p)

    return pairs

def converter_function(pairs):
    return
    new_pairs = []

    for pair in pairs:
        p = pair

        a_letter = replace_pattern(r'\d', '', p[1]).strip()
        b_letter = replace_pattern(r'\d', '', p[3]).strip()
        p[1] = replace_pattern(r'\D', '', p[1]).strip()
        p[3] = replace_pattern(r'\D', '', p[3]).strip()

        # ?
        new_pairs.append([
            64 * (int(p[0]) - 1) + (int(p[1]) * 2) - (1 if a_letter == 'A' else 0),
            64 * (int(p[2]) - 1) + (int(p[3]) * 2) - (1 if b_letter == 'A' else 0)
        ])

    return new_pairs


TABLE = """
A1;66;2.c1
A2;68;2.c2
A3;70;2.c3
A4;72;2.c4
A5;74;2.c5
A6;76;2.c6
A7;78;2.c7
A8;80;2.c8
A9;82;2.c9
A10;84;2.c10
A11;86;2.c11
A12;88;2.c12
A13;90;2.c13
A14;92;2.c14
A15;94;2.c15
A16;96;2.c16
A17;98;2.c17
A18;100;2.c18
A19;102;2.c19
A20;104;2.c20
A21;106;2.c21
A22;108;2.c22
A23;110;2.c23
A24;112;2.c24
A25;114;2.c25
A26;116;2.c26
A27;118;2.c27
A28;120;2.c28
A29;122;2.c29
A30;124;2.c30
A31;126;2.c31
A32;128;2.c32
A33;2;1.c1
A34;4;1.c2
A35;6;1.c3
A36;8;1.c4
A37;10;1.c5
A38;12;1.c6
A39;14;1.c7
A40;16;1.c8
A41;18;1.c9
A42;20;1.c10
A43;22;1.c11
A44;24;1.c12
A45;26;1.c13
A46;28;1.c14
A47;30;1.c15
A48;32;1.c16
A49;34;1.c17
A50;36;1.c18
A51;38;1.c19
A52;40;1.c20
A53;42;1.c21
A54;44;1.c22
A55;46;1.c23
A56;48;1.c24
A57;50;1.c25
A58;52;1.c26
A59;54;1.c27
A60;56;1.c28
A61;58;1.c29
A62;60;1.c30
A63;62;1.c31
A64;64;1.c32
A65;194;4.c1
A66;196;4.c2
A67;198;4.c3
A68;200;4.c4
A69;202;4.c5
A70;204;4.c6
A71;206;4.c7
A72;208;4.c8
A73;210;4.c9
A74;212;4.c10
A75;214;4.c11
A76;216;4.c12
A77;218;4.c13
A78;220;4.c14
A79;222;4.c15
A80;224;4.c16
A81;226;4.c17
A82;228;4.c18
A83;230;4.c19
A84;232;4.c20
A85;234;4.c21
A86;236;4.c22
A87;238;4.c23
A88;240;4.c24
A89;242;4.c25
A90;244;4.c26
A91;246;4.c27
A92;248;4.c28
A93;250;4.c29
A94;252;4.c30
A95;254;4.c31
A96;256;4.c32
A97;130;3.c1
A98;132;3.c2
A99;134;3.c3
A100;136;3.c4
A101;138;3.c5
A102;140;3.c6
A103;142;3.c7
A104;144;3.c8
A105;146;3.c9
A106;148;3.c10
A107;150;3.c11
A108;152;3.c12
A109;154;3.c13
A110;156;3.c14
A111;158;3.c15
A112;160;3.c16
A113;162;3.c17
A114;164;3.c18
A115;166;3.c19
A116;168;3.c20
A117;170;3.c21
A118;172;3.c22
A119;174;3.c23
A120;176;3.c24
A121;178;3.c25
A122;180;3.c26
A123;182;3.c27
A124;184;3.c28
A125;186;3.c29
A126;188;3.c30
A127;190;3.c31
A128;192;3.c32
A129;322;6.c1
A130;324;6.c2
A131;326;6.c3
A132;328;6.c4
A133;330;6.c5
A134;332;6.c6
A135;334;6.c7
A136;336;6.c8
A137;338;6.c9
A138;340;6.c10
A139;342;6.c11
A140;344;6.c12
A141;346;6.c13
A142;348;6.c14
A143;350;6.c15
A144;352;6.c16
A145;354;6.c17
A146;356;6.c18
A147;358;6.c19
A148;360;6.c20
A149;362;6.c21
A150;364;6.c22
A151;366;6.c23
A152;368;6.c24
A153;370;6.c25
A154;372;6.c26
A155;374;6.c27
A156;376;6.c28
A157;378;6.c29
A158;380;6.c30
A159;382;6.c31
A160;384;6.c32
A161;258;5.c1
A162;260;5.c2
A163;262;5.c3
A164;264;5.c4
A165;266;5.c5
A166;268;5.c6
A167;270;5.c7
A168;272;5.c8
A169;274;5.c9
A170;276;5.c10
A171;278;5.c11
A172;280;5.c12
A173;282;5.c13
A174;284;5.c14
A175;286;5.c15
A176;288;5.c16
A177;290;5.c17
A178;292;5.c18
A179;294;5.c19
A180;296;5.c20
A181;298;5.c21
A182;300;5.c22
A183;302;5.c23
A184;304;5.c24
A185;306;5.c25
A186;308;5.c26
A187;310;5.c27
A188;312;5.c28
A189;314;5.c29
A190;316;5.c30
A191;318;5.c31
A192;320;5.c32
A193;450;8.c1
A194;452;8.c2
A195;454;8.c3
A196;456;8.c4
A197;458;8.c5
A198;460;8.c6
A199;462;8.c7
A200;464;8.c8
A201;466;8.c9
A202;468;8.c10
A203;470;8.c11
A204;472;8.c12
A205;474;8.c13
A206;476;8.c14
A207;478;8.c15
A208;480;8.c16
A209;482;8.c17
A210;484;8.c18
A211;486;8.c19
A212;488;8.c20
A213;490;8.c21
A214;492;8.c22
A215;494;8.c23
A216;496;8.c24
A217;498;8.c25
A218;500;8.c26
A219;502;8.c27
A220;504;8.c28
A221;506;8.c29
A222;508;8.c30
A223;510;8.c31
A224;512;8.c32
A225;386;7.c1
A226;388;7.c2
A227;390;7.c3
A228;392;7.c4
A229;394;7.c5
A230;396;7.c6
A231;398;7.c7
A232;400;7.c8
A233;402;7.c9
A234;404;7.c10
A235;406;7.c11
A236;408;7.c12
A237;410;7.c13
A238;412;7.c14
A239;414;7.c15
A240;416;7.c16
A241;418;7.c17
A242;420;7.c18
A243;422;7.c19
A244;424;7.c20
A245;426;7.c21
A246;428;7.c22
A247;430;7.c23
A248;432;7.c24
A249;434;7.c25
A250;436;7.c26
A251;438;7.c27
A252;440;7.c28
A253;442;7.c29
A254;444;7.c30
A255;446;7.c31
A256;448;7.c32
C1;65;2.a1
C2;67;2.a2
C3;69;2.a3
C4;71;2.a4
C5;73;2.a5
C6;75;2.a6
C7;77;2.a7
C8;79;2.a8
C9;81;2.a9
C10;83;2.a10
C11;85;2.a11
C12;87;2.a12
C13;89;2.a13
C14;91;2.a14
C15;93;2.a15
C16;95;2.a16
C17;97;2.a17
C18;99;2.a18
C19;101;2.a19
C20;103;2.a20
C21;105;2.a21
C22;107;2.a22
C23;109;2.a23
C24;111;2.a24
C25;113;2.a25
C26;115;2.a26
C27;117;2.a27
C28;119;2.a28
C29;121;2.a29
C30;123;2.a30
C31;125;2.a31
C32;127;2.a32
C33;1;1.a1
C34;3;1.a2
C35;5;1.a3
C36;7;1.a4
C37;9;1.a5
C38;11;1.a6
C39;13;1.a7
C40;15;1.a8
C41;17;1.a9
C42;19;1.a10
C43;21;1.a11
C44;23;1.a12
C45;25;1.a13
C46;27;1.a14
C47;29;1.a15
C48;31;1.a16
C49;33;1.a17
C50;35;1.a18
C51;37;1.a19
C52;39;1.a20
C53;41;1.a21
C54;43;1.a22
C55;45;1.a23
C56;47;1.a24
C57;49;1.a25
C58;51;1.a26
C59;53;1.a27
C60;55;1.a28
C61;57;1.a29
C62;59;1.a30
C63;61;1.a31
C64;63;1.a32
C65;193;4.a1
C66;195;4.a2
C67;197;4.a3
C68;199;4.a4
C69;201;4.a5
C70;203;4.a6
C71;205;4.a7
C72;207;4.a8
C73;209;4.a9
C74;211;4.a10
C75;213;4.a11
C76;215;4.a12
C77;217;4.a13
C78;219;4.a14
C79;221;4.a15
C80;223;4.a16
C81;225;4.a17
C82;227;4.a18
C83;229;4.a19
C84;231;4.a20
C85;233;4.a21
C86;235;4.a22
C87;237;4.a23
C88;239;4.a24
C89;241;4.a25
C90;243;4.a26
C91;245;4.a27
C92;247;4.a28
C93;249;4.a29
C94;251;4.a30
C95;253;4.a31
C96;255;4.a32
C97;129;3.a1
C98;131;3.a2
C99;133;3.a3
C100;135;3.a4
C101;137;3.a5
C102;139;3.a6
C103;141;3.a7
C104;143;3.a8
C105;145;3.a9
C106;147;3.a10
C107;149;3.a11
C108;151;3.a12
C109;153;3.a13
C110;155;3.a14
C111;157;3.a15
C112;159;3.a16
C113;161;3.a17
C114;163;3.a18
C115;165;3.a19
C116;167;3.a20
C117;169;3.a21
C118;171;3.a22
C119;173;3.a23
C120;175;3.a24
C121;177;3.a25
C122;179;3.a26
C123;181;3.a27
C124;183;3.a28
C125;185;3.a29
C126;187;3.a30
C127;189;3.a31
C128;191;3.a32
C129;321;6.a1
C130;323;6.a2
C131;325;6.a3
C132;327;6.a4
C133;329;6.a5
C134;331;6.a6
C135;333;6.a7
C136;335;6.a8
C137;337;6.a9
C138;339;6.a10
C139;341;6.a11
C140;343;6.a12
C141;345;6.a13
C142;347;6.a14
C143;349;6.a15
C144;351;6.a16
C145;353;6.a17
C146;355;6.a18
C147;357;6.a19
C148;359;6.a20
C149;361;6.a21
C150;363;6.a22
C151;365;6.a23
C152;367;6.a24
C153;369;6.a25
C154;371;6.a26
C155;373;6.a27
C156;375;6.a28
C157;377;6.a29
C158;379;6.a30
C159;381;6.a31
C160;383;6.a32
C161;257;5.a1
C162;259;5.a2
C163;261;5.a3
C164;263;5.a4
C165;265;5.a5
C166;267;5.a6
C167;269;5.a7
C168;271;5.a8
C169;273;5.a9
C170;275;5.a10
C171;277;5.a11
C172;279;5.a12
C173;281;5.a13
C174;283;5.a14
C175;285;5.a15
C176;287;5.a16
C177;289;5.a17
C178;291;5.a18
C179;293;5.a19
C180;295;5.a20
C181;297;5.a21
C182;299;5.a22
C183;301;5.a23
C184;303;5.a24
C185;305;5.a25
C186;307;5.a26
C187;309;5.a27
C188;311;5.a28
C189;313;5.a29
C190;315;5.a30
C191;317;5.a31
C192;319;5.a32
C193;449;8.a1
C194;451;8.a2
C195;453;8.a3
C196;455;8.a4
C197;457;8.a5
C198;459;8.a6
C199;461;8.a7
C200;463;8.a8
C201;465;8.a9
C202;467;8.a10
C203;469;8.a11
C204;471;8.a12
C205;473;8.a13
C206;475;8.a14
C207;477;8.a15
C208;479;8.a16
C209;481;8.a17
C210;483;8.a18
C211;485;8.a19
C212;487;8.a20
C213;489;8.a21
C214;491;8.a22
C215;493;8.a23
C216;495;8.a24
C217;497;8.a25
C218;499;8.a26
C219;501;8.a27
C220;503;8.a28
C221;505;8.a29
C222;507;8.a30
C223;509;8.a31
C224;511;8.a32
C225;385;7.a1
C226;387;7.a2
C227;389;7.a3
C228;391;7.a4
C229;393;7.a5
C230;395;7.a6
C231;397;7.a7
C232;399;7.a8
C233;401;7.a9
C234;403;7.a10
C235;405;7.a11
C236;407;7.a12
C237;409;7.a13
C238;411;7.a14
C239;413;7.a15
C240;415;7.a16
C241;417;7.a17
C242;419;7.a18
C243;421;7.a19
C244;423;7.a20
C245;425;7.a21
C246;427;7.a22
C247;429;7.a23
C248;431;7.a24
C249;433;7.a25
C250;435;7.a26
C251;437;7.a27
C252;439;7.a28
C253;441;7.a29
C254;443;7.a30
C255;445;7.a31
C256;447;7.a32
"""

def build_table():
    global TABLE
    result = {}
    
    for line in TABLE.splitlines():
        if not line:
            continue
            
        parts = line.split(';')
        result[parts[0]] = parts[1:]
    
    return result


if __name__ == '__main__':
    pass
