# -*- coding: utf-8 -*-

import pytest
import bots
import bots.node as node
import bots.inmessage as inmessage
import bots.outmessage as outmessage
from bots.botsconfig import MPATH


''' plugin unitformats
    set bots.ini: max_number_errors = 1
'''
# python 2.6 treats -0 different. in outmessage this is adapted, for inmessage: python 2.6 does this correct

pytestmark = pytest.mark.usefixtures('engine_logging')
testdummy = {MPATH: 'dummy for tests'}
nodedummy = node.Node()


def format_field(edi, *args):
    __tracebackhide__ = True
    field_value = edi._formatfield(*args)

    try:
        edi.checkforerrorlist()
    finally:
        edi.errorlist.clear()
        edi.errorfatal = False

    return field_value


@pytest.mark.unit_test
class TestFormatFieldVariableOutmessage:

    @pytest.fixture(autouse=True)
    def edi(self):
        return outmessage.outmessage_init(messagetype='edifact', editype='edifact')

    def test_out_var_R(self, edi):
        edi.ta_info['lengthnumericbare'] = True
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 3, 'R', True, 0, 0, 'R']

        assert edi._initfield(tfield1) == '0', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '1', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '1', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '1', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00'
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '1', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '1', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '123', 'strip + sign'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '1,23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # exponent
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            assert format_field(edi, '.001', tfield1, testdummy, nodedummy)  # bots adds 0 before dec, thus too big

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'R', True, 0, 5, 'R']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '12345', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '0.1000', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '00001', 'keep leading zeroes'
        assert format_field(edi, '123', tfield2, testdummy, nodedummy) == '00123', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '0000.1', 'add leading zeroes'

        # test exp
        assert format_field(edi, '12E+3', tfield2, testdummy, nodedummy) == '12000', 'Exponent notation not working as input; big E and +'
        assert format_field(edi, '12E3', tfield2, testdummy, nodedummy) == '12000', 'Exponent notation not working as input; big E'
        assert format_field(edi, '12e+3', tfield2, testdummy, nodedummy) == '12000', 'Exponent notation not working as input; little e and +'
        assert format_field(edi, '12e3', tfield2, testdummy, nodedummy) == '12000', 'Exponent notation not working as input; little e'
        assert format_field(edi, '12345E+3', tfield2, testdummy, nodedummy) == '12345000', 'Exponent notation not working as input; exact max size'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        # no negative exponents for R
        tfield3 = ['TEST1', 'M', 8, 'R', True, 3, 5, 'R']
        assert format_field(edi, '12E-3', tfield3, testdummy, nodedummy) == '00.012', 'Exponent notation not working as input; big E and -'
        assert format_field(edi, '12e-3', tfield3, testdummy, nodedummy) == '00.012', 'Exponent notation not working as input; little E and -'
        assert format_field(edi, '12345678E-3', tfield3, testdummy, nodedummy) == '12345.678', 'Period incorrectly counted towards max in lengthnumericbare=True'
        assert format_field(edi, '12345678E-7', tfield3, testdummy, nodedummy) == '1.2345678', 'Period incorrectly counted towards max in lengthnumericbare=True'
        assert format_field(edi, '123456E-7', tfield3, testdummy, nodedummy) == '0.0123456', "Period incorrectly counted towards max in lengthnumericbare=True with leading 0's"
        assert format_field(edi, '1234567E-7', tfield3, testdummy, nodedummy) == '0.1234567', "Period incorrectly counted towards max in lengthnumericbare=True with leading 0"
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E-8', tfield3, testdummy, nodedummy)  # gets 0.12345678, is too big

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield3, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 80, 'R', True, 3, 0, 'R']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '12345678901234560', 'lot of digits'

        # test for length checks if:
        edi.ta_info['lengthnumericbare'] = False
        assert format_field(edi, '-1.45', tfield2, testdummy, nodedummy) == '-1.45', 'just large enough'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12345678', tfield2, testdummy, nodedummy)  # field too large

    def test_out_var_N(self, edi):
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['lengthnumericbare'] = True
        tfield1 = ['TEST1', 'M', 5, 'N', True, 2, 0, 'N']

        assert edi._initfield(tfield1) == '0.00', 'empty string'  # empty strings are not passed anymore to _formatfield 20120325
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '1.00', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '1.00', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '1.00', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0.00', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123.00', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '1.00', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '123.1049', tfield1, testdummy, nodedummy) == '123.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '1.00', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '123.00', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '1,23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield23 = ['TEST1', 'M', 8, 'N', True, 0, 5, 'N']
        assert format_field(edi, '12345.5', tfield23, testdummy, nodedummy) == '12346', 'just large enough'

        tfield2 = ['TEST1', 'M', 8, 'N', True, 2, 5, 'N']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '123.45', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '123.45', 'just large enough'

        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '123.46', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '000.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '001.00', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '012.00', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '000.10', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '178E+3', tfield2, testdummy, nodedummy) == '178000.00', 'add leading zeroes'
        assert format_field(edi, '-178E+3', tfield2, testdummy, nodedummy) == '-178000.00', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '-000.18', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '-000.00', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 80, 'N', True, 3, 0, 'N']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '12345678901234560.000', 'lot of digits'
        assert format_field(edi, '1234567890123456789012345', tfield4, testdummy, nodedummy) == '1234567890123456789012345.000', 'lot of digits'

    def test_out_var_I(self, edi):
        edi.ta_info['lengthnumericbare'] = True
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 5, 'I', True, 2, 0, 'I']

        assert edi._initfield(tfield1) == '0', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '100', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '100', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '100', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-12', 'no zero before dec,sign is OK'  # TODO: puts in front
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '12300', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '100', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '123.1049', tfield1, testdummy, nodedummy) == '12310', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-123', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '100', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '12300', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '123', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end

        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '1300', 'other dec.sig, replace'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'I', True, 2, 5, 'I']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '12345', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '12345', 'just large enough'
        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '12346', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '00010', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '00100', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '01200', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '00010', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '178E+3', tfield2, testdummy, nodedummy) == '17800000', 'add leading zeroes'
        assert format_field(edi, '-178E+3', tfield2, testdummy, nodedummy) == '-17800000', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '-00018', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '-00000', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 80, 'I', True, 3, 0, 'I']
        assert format_field(edi, '123456789012340', tfield4, testdummy, nodedummy) == '123456789012340000', 'lot of digits'

    def test_out_var_D(self, edi):
        tfield1 = ['TEST1', 'M', 20, 'D', True, 0, 0, 'D']

        assert format_field(edi, '20071001', tfield1, testdummy, nodedummy) == '20071001', 'basic'
        assert format_field(edi, '071001', tfield1, testdummy, nodedummy) == '071001', 'basic'
        assert format_field(edi, '99991001', tfield1, testdummy, nodedummy) == '99991001', 'max year'
        assert format_field(edi, '00011001', tfield1, testdummy, nodedummy) == '00011001', 'min year'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2007093112', tfield1, testdummy, nodedummy)  # too long
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '20070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-0070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '70931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931BC', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'OOOOBC', tfield1, testdummy, nodedummy)  # alfanum

    def test_out_var_T(self, edi):
        tfield1 = ['TEST1', 'M', 10, 'T', True, 0, 0, 'T']
        assert format_field(edi, '2359', tfield1, testdummy, nodedummy) == '2359', 'basic'
        assert format_field(edi, '0000', tfield1, testdummy, nodedummy) == '0000', 'basic'
        assert format_field(edi, '000000', tfield1, testdummy, nodedummy) == '000000', 'basic'
        assert format_field(edi, '230000', tfield1, testdummy, nodedummy) == '230000', 'basic'
        assert format_field(edi, '235959', tfield1, testdummy, nodedummy) == '235959', 'basic'
        assert format_field(edi, '123456', tfield1, testdummy, nodedummy) == '123456', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240001', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '126101', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120062', tfield1, testdummy, nodedummy)  # no valid time - python allows 61 secnds?
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240000', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '250001', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12000', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120', tfield1, testdummy, nodedummy)  # no valid time
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931233', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '11PM', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'TIME', tfield1, testdummy, nodedummy)  # alfanum

        tfield2 = ['TEST1', 'M', 4, 'T', True, 0, 4, 'T']
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '230001', tfield2, testdummy, nodedummy)  # time too long

        tfield3 = ['TEST1', 'M', 6, 'T', True, 0, 6, 'T']
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2300', tfield3, testdummy, nodedummy)  # time too short

    def test_out_var_A(self, edi):
        tfield1 = ['TEST1', 'M', 5, 'A', True, 0, 0, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)

        tfield1 = ['TEST1', 'M', 5, 'A', True, 0, 2, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb', 'basic'
        assert format_field(edi, 'aa', tfield1, testdummy, nodedummy) == 'aa', 'basic'
        assert format_field(edi, 'aaa', tfield1, testdummy, nodedummy) == 'aaa', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'a', tfield1, testdummy, nodedummy)  # field too small
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, ' ', tfield1, testdummy, nodedummy)  # field too small
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '', tfield1, testdummy, nodedummy)  # field too small
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)


@pytest.mark.unit_test
class TestFormatFieldFixedOutmessage:

    @pytest.fixture(autouse=True)
    def edi(self):
        return outmessage.outmessage_init(editype='fixed', messagetype='ordersfixed')

    def test_out_fixedR(self, edi):
        edi.ta_info['lengthnumericbare'] = False
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 3, 'R', True, 0, 3, 'R']

        assert edi._initfield(tfield1) == '000', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '001', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '001', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '001', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '000', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-00', 'neg.zero stays neg.zero'

        tfield3 = ['TEST1', 'M', 5, 'R', True, 2, 3, 'R']
        assert format_field(edi, '-0.00', tfield3, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '0.10', tfield3, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'

        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '001', 'leading zeroes are removed'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '001', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '123', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.2', tfield1, testdummy, nodedummy) == '1,2', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.001', tfield1, testdummy, nodedummy)  # bots adds 0 before dec, thus too big

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'R', True, 0, 8, 'R']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '00012345', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '000.1000', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '00000001', 'keep leading zeroes'
        assert format_field(edi, '123', tfield2, testdummy, nodedummy) == '00000123', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '000000.1', 'add leading zeroes'
        assert format_field(edi, '-1.23', tfield2, testdummy, nodedummy) == '-0001.23', 'numeric field at max with minus and decimal sign'

        # test exp
        assert format_field(edi, '12E+3', tfield2, testdummy, nodedummy) == '00012000', 'Incorrect fixed length, 0 filled, scientific notation processing; big E and +'
        assert format_field(edi, '12E3', tfield2, testdummy, nodedummy) == '00012000', 'Incorrect fixed length, 0 filled, scientific notation processing; big E'
        assert format_field(edi, '12e+3', tfield2, testdummy, nodedummy) == '00012000', 'Incorrect fixed length, 0 filled, scientific notation processing; little e and +'
        assert format_field(edi, '12e3', tfield2, testdummy, nodedummy) == '00012000', 'Incorrect fixed length, 0 filled, scientific notation processing; little e'
        assert format_field(edi, '4567E+3', tfield2, testdummy, nodedummy) == '04567000', 'Incorrect fixed length, 0 filled, scientific notation processing'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        # no negative exponents for R
        assert format_field(edi, '12E-3', tfield2, testdummy, nodedummy) == '0000.012', 'Incorrect fixed length, 0 filled, scientific notation processing; big E and -'
        assert format_field(edi, '12e-3', tfield2, testdummy, nodedummy) == '0000.012', 'Incorrect fixed length, 0 filled, scientific notation processing; little e and -'
        assert format_field(edi, '1234567E-3', tfield2, testdummy, nodedummy) == '1234.567', 'Incorrect fixed length, 0 filled, scientific notation processing'
        assert format_field(edi, '1234567E-6', tfield2, testdummy, nodedummy) == '1.234567', 'Incorrect fixed length, 0 filled, scientific notation processing'
        assert format_field(edi, '123456E-6', tfield2, testdummy, nodedummy) == '0.123456', 'Incorrect fixed length, 0 filled, scientific notation processing with leading 0'
        assert format_field(edi, '-12345E-5', tfield2, testdummy, nodedummy) == '-0.12345', 'Incorrect fixed length, 0 filled, scientific notation processing with negative sign'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E-8', tfield2, testdummy, nodedummy)  # gets 0.12345678, is too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'R', True, 3, 30, 'R']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '000000000000012345678901234560', 'lot of digits'

        tfield5 = ['TEST1', 'M', 4, 'R', True, 2, 4, 'R']
        assert format_field(edi, '0.00', tfield5, testdummy, nodedummy) == '0.00', 'lot of digits'

        tfield6 = ['TEST1', 'M', 5, 'R', True, 2, 5, 'R']
        assert format_field(edi, '12.45', tfield6, testdummy, nodedummy) == '12.45', 'lot of digits'

    def test_out_fixedRL(self, edi):
        edi.ta_info['lengthnumericbare'] = False
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 3, 'RL', True, 0, 3, 'R']

        assert edi._initfield(tfield1) == '0  ', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '1  ', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '1  ', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '1  ', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0  ', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0 ', 'neg.zero stays neg.zero'

        tfield3 = ['TEST1', 'M', 5, 'RL', True, 2, 3, 'R']
        assert format_field(edi, '-0.00', tfield3, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '0.10', tfield3, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '1  ', 'leading zeroes are removed'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '1  ', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '123', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.2', tfield1, testdummy, nodedummy) == '1,2', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.001', tfield1, testdummy, nodedummy)  # bots adds 0 before dec, thus too big

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'RL', True, 0, 8, 'R']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '12345   ', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '0.1000  ', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '1       ', 'keep leading zeroes'
        assert format_field(edi, '123', tfield2, testdummy, nodedummy) == '123     ', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '0.1     ', 'add leading zeroes'
        assert format_field(edi, '-1.23', tfield2, testdummy, nodedummy) == '-1.23   ', 'numeric field at max with minus and decimal sign'

        # test exp
        assert format_field(edi, '12E+3', tfield2, testdummy, nodedummy) == '12000   ', 'Incorrect fixed length, space filled, scientific notation processing; big E and +'
        assert format_field(edi, '12E3', tfield2, testdummy, nodedummy) == '12000   ', 'Incorrect fixed length, space filled, scientific notation processing; big E'
        assert format_field(edi, '12e+3', tfield2, testdummy, nodedummy) == '12000   ', 'Incorrect fixed length, space filled, scientific notation processing; little e and +'
        assert format_field(edi, '12e3', tfield2, testdummy, nodedummy) == '12000   ', 'Incorrect fixed length, space filled, scientific notation processing; little e'
        assert format_field(edi, '4567E+3', tfield2, testdummy, nodedummy) == '4567000 ', 'Incorrect fixed length, space filled, scientific notation processing'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        # no negative exponents for R
        assert format_field(edi, '12E-3', tfield2, testdummy, nodedummy) == '0.012   ', 'Incorrect fixed length, space filled, scientific notation processing; big E and -'
        assert format_field(edi, '12e-3', tfield2, testdummy, nodedummy) == '0.012   ', 'Incorrect fixed length, space filled, scientific notation processing; little E and -'
        assert format_field(edi, '1234567E-3', tfield2, testdummy, nodedummy) == '1234.567', 'Incorrect fixed length, space filled, scientific notation processing'
        assert format_field(edi, '1234567E-6', tfield2, testdummy, nodedummy) == '1.234567', 'Incorrect fixed length, space filled, scientific notation processing'
        assert format_field(edi, '123456E-6', tfield2, testdummy, nodedummy) == '0.123456', 'Incorrect fixed length, space filled, scientific notation processing with leading 0'
        assert format_field(edi, '-12345E-5', tfield2, testdummy, nodedummy) == '-0.12345', 'Incorrect fixed length, space filled, scientific notation processing with negative sign'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E-8', tfield2, testdummy, nodedummy)  # gets 0.12345678, is too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'RL', True, 3, 30, 'R']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '12345678901234560             ', 'lot of digits'

        tfield5 = ['TEST1', 'M', 4, 'RL', True, 2, 4, 'N']
        assert format_field(edi, '0.00', tfield5, testdummy, nodedummy) == '0.00', 'lot of digits'

        tfield6 = ['TEST1', 'M', 5, 'RL', True, 2, 5, 'N']
        assert format_field(edi, '12.45', tfield6, testdummy, nodedummy) == '12.45', 'lot of digits'

    def test_out_fixedRR(self, edi):
        edi.ta_info['lengthnumericbare'] = False
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 3, 'RR', True, 0, 3, 'R']

        assert edi._initfield(tfield1) == '  0', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '  1', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '  1', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '  1', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '  0', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == ' -0', 'neg.zero stays neg.zero'

        tfield3 = ['TEST1', 'M', 5, 'RR', True, 2, 3, 'R']
        assert format_field(edi, '-0.00', tfield3, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '0.10', tfield3, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '  1', 'leading zeroes are removed'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '  1', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '123', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.2', tfield1, testdummy, nodedummy) == '1,2', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-.12', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.001', tfield1, testdummy, nodedummy)  # bots adds 0 before dec, thus too big

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'RR', True, 0, 8, 'R']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '   12345', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '  0.1000', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '       1', 'keep leading zeroes'
        assert format_field(edi, '123', tfield2, testdummy, nodedummy) == '     123', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '     0.1', 'add leading zeroes'
        assert format_field(edi, '-1.23', tfield2, testdummy, nodedummy) == '   -1.23', 'numeric field at max with minus and decimal sign'

        # test exp
        assert format_field(edi, '12E+3', tfield2, testdummy, nodedummy) == '   12000', 'Incorrect fixed length, space filled, scientific notation processing; big E and +'
        assert format_field(edi, '12E3', tfield2, testdummy, nodedummy) == '   12000', 'Incorrect fixed length, space filled, scientific notation processing; big E'
        assert format_field(edi, '12e+3', tfield2, testdummy, nodedummy) == '   12000', 'Incorrect fixed length, space filled, scientific notation processing; little e and +'
        assert format_field(edi, '12e3', tfield2, testdummy, nodedummy) == '   12000', 'Incorrect fixed length, space filled, scientific notation processing; little e'
        assert format_field(edi, '4567E+3', tfield2, testdummy, nodedummy) == ' 4567000', 'Incorrect fixed length, space filled, scientific notation processing'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        # no negative exponents for R
        assert format_field(edi, '12E-3', tfield2, testdummy, nodedummy) == '   0.012', 'Incorrect fixed length, space filled, scientific notation processing; big E and -'
        assert format_field(edi, '12e-3', tfield2, testdummy, nodedummy) == '   0.012', 'Incorrect fixed length, space filled, scientific notation processing; little e and -'
        assert format_field(edi, '1234567E-3', tfield2, testdummy, nodedummy) == '1234.567', 'Incorrect fixed length, space filled, scientific notation processing'
        assert format_field(edi, '1234567E-6', tfield2, testdummy, nodedummy) == '1.234567', 'Incorrect fixed length, space filled, scientific notation processing'
        assert format_field(edi, '123456E-6', tfield2, testdummy, nodedummy) == '0.123456', 'Incorrect fixed length, space filled, scientific notation processing with leading 0'
        assert format_field(edi, '-12345E-5', tfield2, testdummy, nodedummy) == '-0.12345', 'Incorrect fixed length, space filled, scientific notation processing with negative sign'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E-8', tfield2, testdummy, nodedummy)  # gets 0.12345678, is too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12345678E+3', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'RR', True, 3, 30, 'R']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '             12345678901234560', 'lot of digits'

        tfield5 = ['TEST1', 'M', 4, 'RR', True, 2, 4, 'N']
        assert format_field(edi, '0.00', tfield5, testdummy, nodedummy) == '0.00', 'lot of digits'

        tfield6 = ['TEST1', 'M', 5, 'RR', True, 2, 5, 'N']
        assert format_field(edi, '12.45', tfield6, testdummy, nodedummy) == '12.45', 'lot of digits'

    def test_out_fixedN(self, edi):
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['lengthnumericbare'] = False
        tfield1 = ['TEST1', 'M', 5, 'N', True, 2, 5, 'N']

        assert edi._initfield(tfield1) == '00.00', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '01.00', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '01.00', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '01.00', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '00.00', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '01.00', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '00.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '12.1049', tfield1, testdummy, nodedummy) == '12.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '01.00', 'strips leading zeroes if possible'
        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '13.00', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '01,23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123.1049', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'N', True, 2, 8, 'N']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '00123.45', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '00123.45', 'just large enough'
        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '00123.46', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '00000.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '00001.00', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '00012.00', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '00000.10', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '78E+3', tfield2, testdummy, nodedummy) == '78000.00', 'add leading zeroes'
        assert format_field(edi, '-8E+3', tfield2, testdummy, nodedummy) == '-8000.00', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '-0000.18', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '-0000.00', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'N', True, 3, 30, 'N']
        assert format_field(edi, '1234567890123456', tfield4, testdummy, nodedummy) == '00000000001234567890123456.000', 'lot of digits'

        # test N format, zero decimals
        tfield7 = ['TEST1', 'M', 5, 'N', True, 0, 5, 'N']
        assert format_field(edi, '12345', tfield7, testdummy, nodedummy) == '12345', ''
        assert format_field(edi, '1.234', tfield7, testdummy, nodedummy) == '00001', ''
        assert format_field(edi, '123.4', tfield7, testdummy, nodedummy) == '00123', ''
        assert format_field(edi, '0.0', tfield7, testdummy, nodedummy) == '00000', ''

    def test_out_fixedNL(self, edi):
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['lengthnumericbare'] = False
        tfield1 = ['TEST1', 'M', 5, 'NL', True, 2, 5, 'N']

        assert edi._initfield(tfield1) == '0.00 ', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '1.00 ', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '1.00 ', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '1.00 ', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0.00 ', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '1.00 ', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '0.10 ', 'keep zeroes after last dec.digit'
        assert format_field(edi, '12.1049', tfield1, testdummy, nodedummy) == '12.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '1.00 ', 'strips leading zeroes if possible'
        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '13.00', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '1,23 ', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123.1049', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'NL', True, 2, 8, 'N']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '123.45  ', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '123.45  ', 'just large enough'
        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '123.46  ', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '0.10    ', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '1.00    ', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '12.00   ', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '0.10    ', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '78E+3', tfield2, testdummy, nodedummy) == '78000.00', 'add leading zeroes'
        assert format_field(edi, '-8E+3', tfield2, testdummy, nodedummy) == '-8000.00', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '-0.18   ', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '-0.00   ', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'NL', True, 3, 30, 'N']
        assert format_field(edi, '1234567890123456', tfield4, testdummy, nodedummy) == '1234567890123456.000          ', 'lot of digits'

        # test N format, zero decimals
        tfield7 = ['TEST1', 'M', 5, 'NL', True, 0, 5, 'N']
        assert format_field(edi, '12345', tfield7, testdummy, nodedummy) == '12345', ''
        assert format_field(edi, '1.234', tfield7, testdummy, nodedummy) == '1    ', ''
        assert format_field(edi, '123.4', tfield7, testdummy, nodedummy) == '123  ', ''
        assert format_field(edi, '0.0', tfield7, testdummy, nodedummy) == '0    ', ''

    def test_out_fixedNR(self, edi):
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['lengthnumericbare'] = False
        tfield1 = ['TEST1', 'M', 5, 'NR', True, 2, 5, 'N']

        assert edi._initfield(tfield1) == ' 0.00', 'empty string'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == ' 1.00', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == ' 1.00', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == ' 1.00', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == ' 0.00', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == ' 1.00', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == ' 0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '12.1049', tfield1, testdummy, nodedummy) == '12.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == ' 1.00', 'strips leading zeroes if possible'
        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '13.00', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == ' 1,23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123.1049', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'NR', True, 2, 8, 'N']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '  123.45', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '  123.45', 'just large enough'
        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '  123.46', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '    0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '    1.00', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '   12.00', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '    0.10', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '78E+3', tfield2, testdummy, nodedummy) == '78000.00', 'add leading zeroes'
        assert format_field(edi, '-8E+3', tfield2, testdummy, nodedummy) == '-8000.00', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '   -0.18', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '   -0.00', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 30, 'NR', True, 3, 30, 'N']
        assert format_field(edi, '1234567890123456', tfield4, testdummy, nodedummy) == '          1234567890123456.000', 'lot of digits'

        # test N format, zero decimals
        tfield7 = ['TEST1', 'M', 5, 'NR', True, 0, 5, 'N']
        assert format_field(edi, '12345', tfield7, testdummy, nodedummy) == '12345', ''
        assert format_field(edi, '1.234', tfield7, testdummy, nodedummy) == '    1', ''
        assert format_field(edi, '123.4', tfield7, testdummy, nodedummy) == '  123', ''
        assert format_field(edi, '0.0', tfield7, testdummy, nodedummy) == '    0', ''

    def test_out_fixedI(self, edi):
        edi.ta_info['lengthnumericbare'] = False
        edi.ta_info['decimaal'] = '.'
        tfield1 = ['TEST1', 'M', 5, 'I', True, 2, 5, 'I']

        assert edi._initfield(tfield1) == '00000', 'empty string is initialised as 00000'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '00100', 'basic'
        assert format_field(edi, ' 1', tfield1, testdummy, nodedummy) == '00100', 'basic'
        assert format_field(edi, '1 ', tfield1, testdummy, nodedummy) == '00100', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '00000', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0000', 'neg.zero stays neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0000', ''
        assert format_field(edi, '-0.001', tfield1, testdummy, nodedummy) == '-0000', ''
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0012', 'no zero before dec,sign is OK'  # TODO: puts  in front
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '12300', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '00100', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '00010', 'keep zeroes after last dec.digit'
        assert format_field(edi, '123.1049', tfield1, testdummy, nodedummy) == '12310', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-0123', 'numeric field at max with minus and decimal sign'
        assert format_field(edi, '0001', tfield1, testdummy, nodedummy) == '00100', 'strips leading zeroes if possible'
        assert format_field(edi, '+123', tfield1, testdummy, nodedummy) == '12300', 'strips leading zeroes if possible'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '00123', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234.56', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123-', tfield1, testdummy, nodedummy)  # '-' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # '+' in middle of number (no exp)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no num
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no num

        # test filling up to min length
        tfield2 = ['TEST1', 'M', 8, 'I', True, 2, 8, 'I']
        assert format_field(edi, '123.45', tfield2, testdummy, nodedummy) == '00012345', 'just large enough'
        assert format_field(edi, '123.4549', tfield2, testdummy, nodedummy) == '00012345', 'just large enough'
        assert format_field(edi, '123.455', tfield2, testdummy, nodedummy) == '00012346', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '00000010', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '00000100', 'keep leading zeroes'
        assert format_field(edi, '12', tfield2, testdummy, nodedummy) == '00001200', 'add leading zeroes'
        assert format_field(edi, '.1', tfield2, testdummy, nodedummy) == '00000010', 'add leading zeroes'

        # test exp; bots tries to convert to normal
        assert format_field(edi, '178E+3', tfield2, testdummy, nodedummy) == '17800000', 'add leading zeroes'
        assert format_field(edi, '-17E+3', tfield2, testdummy, nodedummy) == '-1700000', 'add leading zeroes'
        assert format_field(edi, '-178e-3', tfield2, testdummy, nodedummy) == '-0000018', 'add leading zeroes'
        assert format_field(edi, '-178e-5', tfield2, testdummy, nodedummy) == '-0000000', 'add leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '178E+4', tfield2, testdummy, nodedummy)  # too big with exp

        tfield4 = ['TEST1', 'M', 80, 'I', True, 3, 0, 'I']
        assert format_field(edi, '123456789012340', tfield4, testdummy, nodedummy) == '123456789012340000', 'lot of digits'

    def test_out_fixedD(self, edi):
        tfield1 = ['TEST1', 'M', 8, 'D', True, 0, 8, 'D']
        assert format_field(edi, '20071001', tfield1, testdummy, nodedummy) == '20071001', 'basic'
        assert format_field(edi, '99991001', tfield1, testdummy, nodedummy) == '99991001', 'max year'
        assert format_field(edi, '00011001', tfield1, testdummy, nodedummy) == '00011001', 'min year'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2007093112', tfield1, testdummy, nodedummy)  # too long
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '20070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-0070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '70931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931BC', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'OOOOBC', tfield1, testdummy, nodedummy)  # alfanum

        tfield2 = ['TEST1', 'M', 6, 'D', True, 0, 6, 'D']
        assert format_field(edi, '071001', tfield2, testdummy, nodedummy) == '071001', 'basic'

    def test_out_fixedT(self, edi):
        tfield1 = ['TEST1', 'M', 4, 'T', True, 0, 4, 'T']
        assert format_field(edi, '2359', tfield1, testdummy, nodedummy) == '2359', 'basic'
        assert format_field(edi, '0000', tfield1, testdummy, nodedummy) == '0000', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2401', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1261', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1262', tfield1, testdummy, nodedummy)  # python allows 61 seconds?
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2400', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2501', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1200', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '093123', tfield1, testdummy, nodedummy)  # too long
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '11PM', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'TIME', tfield1, testdummy, nodedummy)  # alfanum

        tfield2 = ['TEST1', 'M', 6, 'T', True, 0, 6, 'T']
        assert format_field(edi, '000000', tfield2, testdummy, nodedummy) == '000000', 'basic'
        assert format_field(edi, '230000', tfield2, testdummy, nodedummy) == '230000', 'basic'
        assert format_field(edi, '235959', tfield2, testdummy, nodedummy) == '235959', 'basic'
        assert format_field(edi, '123456', tfield2, testdummy, nodedummy) == '123456', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240001', tfield2, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '126101', tfield2, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120062', tfield2, testdummy, nodedummy)  # python allows 61 secnds?
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240000', tfield2, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '250001', tfield2, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12000', tfield2, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120', tfield2, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931233', tfield2, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1100PM', tfield2, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '11TIME', tfield2, testdummy, nodedummy)  # alfanum

    def test_out_fixedA(self, edi):
        tfield1 = ['TEST1', 'M', 5, 'A', True, 0, 5, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, 'ab   ', tfield1, testdummy, nodedummy) == 'ab   ', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb  ', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)

        tfield1 = ['TEST1', 'M', 5, 'A', True, 0, 5, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, 'ab   ', tfield1, testdummy, nodedummy) == 'ab   ', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb  ', 'basic'
        assert format_field(edi, 'a', tfield1, testdummy, nodedummy) == 'a    ', 'basic'
        assert format_field(edi, '  ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, '     ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, ' ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '     ', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)

    def test_out_fixedAR(self, edi):
        tfield1 = ['TEST1', 'M', 5, 'AR', True, 0, 5, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, 'ab ', tfield1, testdummy, nodedummy) == '  ab ', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == '  a\tb', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)

        tfield1 = ['TEST1', 'M', 5, 'AR', True, 0, 5, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, 'ab ', tfield1, testdummy, nodedummy) == '  ab ', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == '  a\tb', 'basic'
        assert format_field(edi, 'a', tfield1, testdummy, nodedummy) == '    a', 'basic'
        assert format_field(edi, '  ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, '     ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, ' ', tfield1, testdummy, nodedummy) == '     ', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '     ', 'basic'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)


@pytest.mark.unit_test
class TestFormatFieldInmessage:

    # both var and fixed fields are tested. Is not much difference (white-box testing)
    @pytest.fixture(autouse=True)
    def edi(self):
        # need to have a inmessage-object for tests.
        return inmessage.Inmessage({'messagetype': 'edifact', 'editype': 'edifact'})

    def test_in_R(self, edi):
        edi.ta_info['lengthnumericbare'] = True
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['triad'] = ''
        tfield1 = ['TEST1', 'M', 3, 'N', True, 0, 0, 'R']

        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '0', 'empty numeric string is accepted, is zero'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '1', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0', 'keep neg.zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', 'keep neg.zero, keep decimals'
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '123', 'numeric field at max'
        assert format_field(edi, '001', tfield1, testdummy, nodedummy) == '1', 'leading zeroes are removed'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '0.10', 'keep decimal zeroes'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'

        edi.ta_info['decimaal'] = ','
        assert format_field(edi, '1,23', tfield1, testdummy, nodedummy) == '1.23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0001', tfield1, testdummy, nodedummy)  # leading zeroes; field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' at end of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # exponent

        # test field to short
        tfield2 = ['TEST1', 'M', 8, 'N', True, 0, 5, 'R']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '12345', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '0.1000', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00001', tfield2, testdummy, nodedummy) == '1', 'remove leading zeroes'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1235', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12.34', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-.', tfield2, testdummy, nodedummy)  # field too short

        # WARN: dubious tests. This is Bots filosophy: be flexible in input, be right in output.
        assert format_field(edi, '123-', tfield1, testdummy, nodedummy) == '-123', 'numeric field minus at end'
        assert format_field(edi, '.001', tfield1, testdummy, nodedummy) == '0.001', 'if no zero before dec.sign, length>max.length'
        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '13', 'plus is allowed'  # WARN: if plus used, plus is countd in length!!
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12E+3', tfield2, testdummy, nodedummy)  # field too large

        tfield4 = ['TEST1', 'M', 8, 'N', True, 3, 0, 'R']
        assert format_field(edi, '123.4561', tfield4, testdummy, nodedummy) == '123.4561', 'no check for to many digits incoming'  # should round here?

        tfield4 = ['TEST1', 'M', 80, 'N', True, 3, 0, 'R']
        assert format_field(edi, '12345678901234560', tfield4, testdummy, nodedummy) == '12345678901234560', 'lot of digits'

        edi.ta_info['lengthnumericbare'] = False
        assert format_field(edi, '-1.45', tfield2, testdummy, nodedummy) == '-1.45', 'just large enough'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12345678', tfield2, testdummy, nodedummy)  # field too large

    def test_in_N(self, edi):
        edi.ta_info['lengthnumericbare'] = True
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['triad'] = ','
        tfield1 = ['TEST1', 'M', 3, 'R', True, 2, 0, 'N']

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '', tfield1, testdummy, nodedummy)  # empty string
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1', tfield1, testdummy, nodedummy)  # empty string
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0', tfield1, testdummy, nodedummy)  # empty string
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-0', tfield1, testdummy, nodedummy)  # empty string
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '01.00', tfield1, testdummy, nodedummy)  # empty string

        assert format_field(edi, '1.00', tfield1, testdummy, nodedummy) == '1.00', 'basic'
        assert format_field(edi, '0.00', tfield1, testdummy, nodedummy) == '0.00', 'zero stays zero'
        assert format_field(edi, '-0.00', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-.12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '1.23', tfield1, testdummy, nodedummy) == '1.23', 'numeric field at max'
        assert format_field(edi, '0.10', tfield1, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-1.23', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field at max with minus and decimal sign'

        edi.ta_info['decimaal'] = ','
        edi.ta_info['triad'] = ''
        assert format_field(edi, '1,23-', tfield1, testdummy, nodedummy) == '-1.23', 'other dec.sig, replace'

        edi.ta_info['decimaal'] = '.'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0001', tfield1, testdummy, nodedummy)  # leading zeroes; field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1.234', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1,3', tfield1, testdummy, nodedummy)  # ',', where ',' is not traid sep.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '13+', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0.100', tfield1, testdummy, nodedummy)  # field too big
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1E3', tfield1, testdummy, nodedummy)  # no exp
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '.', tfield1, testdummy, nodedummy)  # no exp
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # no exp

        # test field to short
        tfield2 = ['TEST1', 'M', 8, 'R', True, 4, 5, 'N']
        assert format_field(edi, '1.2345', tfield2, testdummy, nodedummy) == '1.2345', 'just large enough'
        assert format_field(edi, '0.1000', tfield2, testdummy, nodedummy) == '0.1000', 'keep zeroes after last dec.digit'
        assert format_field(edi, '001.1234', tfield2, testdummy, nodedummy) == '1.1234', 'remove leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1235', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12.34', tfield2, testdummy, nodedummy)  # field too short

        # WARN: dubious tests. This is Bots filosophy: be flexible in input, be right in output.
        assert format_field(edi, '1234.1234-', tfield2, testdummy, nodedummy) == '-1234.1234', 'numeric field - minus at end'
        assert format_field(edi, '.01', tfield1, testdummy, nodedummy) == '0.01', 'if no zero before dec.sign, length>max.length'
        assert format_field(edi, '+13.1234', tfield2, testdummy, nodedummy) == '13.1234', 'plus is allowed'  # WARN: if plus used, plus is counted in length!!

        tfield3 = ['TEST1', 'M', 18, 'R', True, 0, 0, 'N']  # @UnusedVariable
        tfield4 = ['TEST1', 'M', 8, 'R', True, 3, 0, 'N']
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123.4561', tfield4, testdummy, nodedummy)  # to many digits

    def test_in_I(self, edi):
        edi.ta_info['lengthnumericbare'] = True
        edi.ta_info['decimaal'] = '.'
        edi.ta_info['triad'] = ''
        tfield1 = ['TEST1', 'M', 5, 'I', True, 2, 0, 'I']

        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '0.00', 'empty numeric is accepted, is zero'
        assert format_field(edi, '123', tfield1, testdummy, nodedummy) == '1.23', 'basic'
        assert format_field(edi, '1', tfield1, testdummy, nodedummy) == '0.01', 'basic'
        assert format_field(edi, '0', tfield1, testdummy, nodedummy) == '0.00', 'zero stays zero'
        assert format_field(edi, '-0', tfield1, testdummy, nodedummy) == '-0.00', 'neg.zero stays neg.zero'
        assert format_field(edi, '-000', tfield1, testdummy, nodedummy) == '-0.00', ''
        assert format_field(edi, '-12', tfield1, testdummy, nodedummy) == '-0.12', 'no zero before dec,sign is OK'
        assert format_field(edi, '12345', tfield1, testdummy, nodedummy) == '123.45', 'numeric field at max'
        assert format_field(edi, '00001', tfield1, testdummy, nodedummy) == '0.01', 'leading zeroes are removed'
        assert format_field(edi, '010', tfield1, testdummy, nodedummy) == '0.10', 'keep zeroes after last dec.digit'
        assert format_field(edi, '-99123', tfield1, testdummy, nodedummy) == '-991.23', 'numeric field at max with minus and decimal sign'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123456', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '000100', tfield1, testdummy, nodedummy)  # field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '000001', tfield1, testdummy, nodedummy)  # leading zeroes; field too large
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12<3', tfield1, testdummy, nodedummy)  # wrong char
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12-3', tfield1, testdummy, nodedummy)  # '-' in middel of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12,3', tfield1, testdummy, nodedummy)  # ','.
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12+3', tfield1, testdummy, nodedummy)  # '+' in middle of number
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '123+', tfield1, testdummy, nodedummy)  # '+'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12E+3', tfield1, testdummy, nodedummy)  # '+'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-', tfield1, testdummy, nodedummy)  # only -

        # test field to short
        tfield2 = ['TEST1', 'M', 8, 'I', True, 2, 5, 'I']
        assert format_field(edi, '12345', tfield2, testdummy, nodedummy) == '123.45', 'just large enough'
        assert format_field(edi, '10000', tfield2, testdummy, nodedummy) == '100.00', 'keep zeroes after last dec.digit'
        assert format_field(edi, '00100', tfield2, testdummy, nodedummy) == '1.00', 'remove leading zeroes'
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '1235', tfield2, testdummy, nodedummy)  # field too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-1234', tfield2, testdummy, nodedummy)  # field too short

        tfield3 = ['TEST1', 'M', 18, 'I', True, 0, 0, 'I']
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '12E+3', tfield3, testdummy, nodedummy)  # no exponent

        # WARN: dubious tests. This is Bots filosophy: be flexible in input, be right in output.
        assert format_field(edi, '123-', tfield1, testdummy, nodedummy) == '-1.23', 'numeric field minus at end'
        assert format_field(edi, '+13', tfield1, testdummy, nodedummy) == '0.13', 'plus is allowed'  # WARN: if plus used, plus is countd in length!!

    def test_in_D(self, edi):
        tfield1 = ['TEST1', 'M', 20, 'D', True, 0, 0, 'D']
        assert format_field(edi, '20071001', tfield1, testdummy, nodedummy) == '20071001', 'basic'
        assert format_field(edi, '071001', tfield1, testdummy, nodedummy) == '071001', 'basic'
        assert format_field(edi, '99991001', tfield1, testdummy, nodedummy) == '99991001', 'max year'
        assert format_field(edi, '00011001', tfield1, testdummy, nodedummy) == '00011001', 'min year'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '2007093112', tfield1, testdummy, nodedummy)  # too long
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '20070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-0070931', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '70931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '0931BC', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'OOOOBC', tfield1, testdummy, nodedummy)  # alfanum

    def test_in_T(self, edi):
        tfield1 = ['TEST1', 'M', 10, 'T', True, 0, 0, 'T']
        assert format_field(edi, '2359', tfield1, testdummy, nodedummy) == '2359', 'basic'
        assert format_field(edi, '0000', tfield1, testdummy, nodedummy) == '0000', 'basic'
        assert format_field(edi, '000000', tfield1, testdummy, nodedummy) == '000000', 'basic'
        assert format_field(edi, '230000', tfield1, testdummy, nodedummy) == '230000', 'basic'
        assert format_field(edi, '235959', tfield1, testdummy, nodedummy) == '235959', 'basic'
        assert format_field(edi, '123456', tfield1, testdummy, nodedummy) == '123456', 'basic'
        assert format_field(edi, '0931233', tfield1, testdummy, nodedummy) == '0931233', 'basic'
        assert format_field(edi, '09312334', tfield1, testdummy, nodedummy) == '09312334', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240001', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '126101', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120062', tfield1, testdummy, nodedummy)  # python allows 61 seconds?
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '240000', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '250001', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '-12000', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '120', tfield1, testdummy, nodedummy)  # too short
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '11PM', tfield1, testdummy, nodedummy)  # alfanum
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'TIME', tfield1, testdummy, nodedummy)  # alfanum

    def test_in_A(self, edi):
        tfield1 = ['TEST1', 'M', 5, 'A', True, 0, 0, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '', 'basic'
        assert format_field(edi, '', tfield1, testdummy, nodedummy) == '', 'basic'

        # strings are stripped before formatfield
        assert format_field(edi, '   ab', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, 'ab   ', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, '\tab', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, 'ab\t', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'ab    ', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '    ab', tfield1, testdummy, nodedummy)

        tfield1 = ['TEST1', 'M', 5, 'T', True, 0, 2, 'A']
        assert format_field(edi, 'abcde', tfield1, testdummy, nodedummy) == 'abcde', 'basic'

        # strings are stripped before formatfield
        assert format_field(edi, '  ab', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, 'ab   ', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, '\tab', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, 'ab\t', tfield1, testdummy, nodedummy) == 'ab', 'basic'
        assert format_field(edi, '  ', tfield1, testdummy, nodedummy) == '', 'basic'
        assert format_field(edi, 'a\tb', tfield1, testdummy, nodedummy) == 'a\tb', 'basic'

        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'a', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'abcdef', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, 'ab    ', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '    ab', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, ' ', tfield1, testdummy, nodedummy)
        with pytest.raises(bots.botslib.MessageError):
            format_field(edi, '', tfield1, testdummy, nodedummy)
