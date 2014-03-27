import logging
import re

from Vintageous import local_logger
from Vintageous.vi import inputs
from Vintageous.vi import utils
from Vintageous.vi.utils import input_types
from Vintageous.vi.utils import modes
from Vintageous.vi import commands


_logger = local_logger(__name__)


class mapping_scopes:
    """
    Scopes for mappings.
    """
    DEFAULT =      0
    USER =         1
    PLUGIN =       2
    NAME_SPACE =   3
    LEADER =       4
    LOCAL_LEADER = 5


class seqs:
    """
    Vim's built-in key sequences plus Sublime Text 3 staple commands.

    These are the sequences of key presses known to Vintageous. Any other
    sequence pressed will be treated as 'unmapped'.
    """

    A =                            'a'
    ALT_CTRL_P =                   '<C-M-p>'
    AMPERSAND =                    '&'
    AW =                           'aw'
    B =                            'b'
    GE =                           'ge'
    UP =                           '<up>'
    DOWN =                         '<down>'
    LEFT =                         '<left>'
    RIGHT =                        '<right>'
    HOME =                         '<home>'
    END =                          '<end>'
    BACKTICK =                     '`'
    BIG_A =                        'A'
    SPACE =                        '<space>'
    BIG_B =                        'B'
    CTRL_E =                       '<C-e>'
    CTRL_Y =                       '<C-y>'
    BIG_C =                        'C'
    BIG_D =                        'D'
    GH =                           'gh'
    G_BIG_H =                      'gH'
    BIG_E =                        'E'
    BIG_F =                        'F'
    BIG_G =                        'G'
    CTRL_W =                       '<C-w>'
    CTRL_W_Q =                     '<C-w>q'

    CTRL_W_V =                     '<C-w>v'
    CTRL_W_L =                     '<C-w>l'
    CTRL_W_BIG_L =                 '<C-w>L'
    CTRL_K =                       '<C-k>'
    CTRL_K_CTRL_B =                '<C-k><C-b>'
    CTRL_BIG_F =                   '<C-F>'
    CTRL_BIG_P =                   '<C-P>'
    CTRL_W_H =                     '<C-w>h'
    Q =                            'q'
    AT =                           '@'
    CTRL_W_BIG_H =                 '<C-w>H'
    BIG_H =                        'H'

    BIG_J =                        'J'
    BIG_Z =                        'Z'
    G_BIG_J =                      'gJ'
    CTRL_R=                        '<C-r>'
    CTRL_R_EQUAL =                 '<C-r>='
    CTRL_A =                       '<C-a>'
    CTRL_X =                       '<C-x>'
    Z =                            'z'
    Z_ENTER =                      'z<cr>'
    ZT =                           'zt'
    ZZ =                           'zz'
    Z_MINUS =                      'z-'
    ZB =                           'zb'

    BIG_I =                        'I'
    BIG_Z_BIG_Z =                  'ZZ'
    BIG_Z_BIG_Q =                  'ZQ'
    GV =                           'gv'
    BIG_J =                        'J'
    BIG_K =                        'K'
    BIG_L =                        'L'
    BIG_M =                        'M'
    BIG_N =                        'N'
    BIG_O =                        'O'
    BIG_P =                        'P'
    BIG_Q =                        'Q'
    BIG_R =                        'R'
    BIG_S =                        'S'
    BIG_T =                        'T'
    BIG_U =                        'U'
    BIG_V =                        'V'
    BIG_W =                        'W'
    BIG_X =                        'X'
    BIG_Y =                        'Y'
    BIG_Z =                        'Z'
    C =                            'c'
    CC =                           'cc'
    COLON =                        ':'
    COMMA =                        ','
    CTRL_D =                       '<C-d>'
    CTRL_F12 =                     '<C-f12>'
    F11 =                          'f11'
    CTRL_l =                       '<C-l>'
    CTRL_B =                       '<C-b>'
    CTRL_F =                       '<C-f>'
    CTRL_G =                       '<C-g>'
    CTRL_P =                       '<C-p>'
    CTRL_U =                       '<C-u>'
    CTRL_V =                       '<C-v>'
    D =                            'd'
    DD =                           'dd'
    DOLLAR =                       '$'
    DOT =                          '.'
    DOUBLE_QUOTE =                 '"'
    E =                            'e'
    ENTER =                        '<cr>' # Or rather <Enter>?
    SHIFT_ENTER =                  '<S-cr>'
    EQUAL =                        '='
    EQUAL_EQUAL =                  '=='
    ESC =                          '<esc>'
    F =                            'f'
    F1 =                           '<f1>'
    F10 =                          '<f10>'
    F11 =                          '<f11>'
    F12 =                          '<f12>'
    F12 =                          '<f12>'
    F13 =                          '<f13>'
    F14 =                          '<f14>'
    F15 =                          '<f15>'
    F2 =                           '<f2>'
    F3 =                           '<f3>'
    F6 =                           '<f6>'
    SHIFT_F2 =                     '<S-f2>'
    SHIFT_F3 =                     '<S-f3>'
    SHIFT_F4 =                     '<S-f4>'
    F4 =                           '<f4>'
    F5 =                           '<f5>'
    F6 =                           '<f6>'
    F7 =                           '<f7>'
    F8 =                           '<f8>'
    F9 =                           '<f9>'
    CTRL_F2 =                      '<C-f2>'
    CTRL_SHIFT_F2 =                '<C-S-f2>'
    G =                            'g'
    G_BIG_D =                      'gD'
    G_BIG_U =                      'gU'
    G_BIG_U_BIG_U =                'gUU'
    G_BIG_U_G_BIG_U =              'gUgU'
    G_TILDE =                      'g~'
    G_TILDE_G_TILDE =              'g~g~'
    G_TILDE_TILDE =                'g~~'
    G_UNDERSCORE =                 'g_'
    GD =                           'gd'
    GG =                           'gg'
    GJ =                           'gj'
    GK =                           'gk'
    GQ =                           'gq'
    GT =                           'gt'
    G_BIG_T =                      'gT'
    GU =                           'gu'
    GUGU =                         'gugu'
    GUU =                          'guu'
    GREATER_THAN =                 '>'
    GREATER_THAN_GREATER_THAN =    '>>'
    H =                            'h'
    HAT =                          '^'
    I =                            'i'
    J =                            'j'
    K =                            'k'
    L =                            'l'
    LEFT_BRACE =                   '{'
    LEFT_SQUARE_BRACKET =          '['
    LEFT_PAREN =                   '('
    LESS_THAN =                    '<lt>'
    LESS_THAN_LESS_THAN =          '<lt><lt>'
    M =                            'm'
    N =                            'n'
    O =                            'o'
    P =                            'p'
    OCTOTHORP =                    '#'
    PERCENT =                      '%'
    PIPE =                         '|'
    QUESTION_MARK =                '?'
    QUOTE =                        "'"
    QUOTE_QUOTE =                  "''"
    R =                            'r'
    RIGHT_BRACE =                  '}'
    RIGHT_SQUARE_BRACKET =         ']'
    RIGHT_PAREN =                  ')'
    S =                            's'
    SEMICOLON =                    ';'
    SHIFT_CTRL_F12 =               '<C-S-f12>'
    SLASH =                        '/'
    STAR =                         '*'
    T =                            't'
    TAB =                          '<tab>'
    TILDE =                        '~'
    U =                            'u'
    UNDERSCORE =                   '_'
    V =                            'v'
    W =                            'w'
    X =                            'x'
    Y =                            'y'
    YY =                           'yy'
    ZERO =                         '0'


def seq_to_command(state, seq, mode=None):
    """
    Returns the command definition mapped to @seq, or a 'missing' command
    if none is found.

    @mode
        Forces the use of this mode instead of the global state's.
    """
    mode = mode or state.mode

    _logger().info('[seq_to_command] state/seq: {0}/{1}'.format(mode, seq))

    if state.mode in mappings:
        command = mappings[mode].get(seq, commands.ViMissingCommandDef())
        return command

    return commands.ViMissingCommandDef()


# Mappings 'key sequence' ==> 'command definition'
#
# 'key sequence' is a sequence of key presses.
#
mappings = {
    modes.NORMAL: {
        seqs.B:                             commands.ViMoveByWordsBackward(),
        seqs.A:                             commands.ViInsertAfterChar(),
        seqs.BIG_A:                         commands.ViInsertAtEol(),
        seqs.BIG_B:                         commands.ViMoveByBigWordsBackward(),
        seqs.BIG_C:                         commands.ViChangeToEol(),
        seqs.BIG_D:                         commands.ViDeleteToEol(),
        seqs.BIG_E:                         commands.ViMoveByBigWordEnds(),
        seqs.BIG_F:                         commands.ViSearchCharBackward(inclusive=True),
        seqs.BIG_G:                         commands.ViGotoEof(),
        seqs.BIG_H:                         commands.ViGotoScreenTop(),
        seqs.BIG_I:                         commands.ViInsertAtBol(),
        seqs.BIG_J:                         commands.ViJoinLines(),
        seqs.ALT_CTRL_P:                    commands.StShowSwitchProject(),
        seqs.AT:                            commands.ViOpenMacrosForRepeating(),
        seqs.BACKTICK:                      commands.ViGotoExactMarkXpos(),
        seqs.BIG_L:                         commands.ViGotoScreenBottom(),
        seqs.BIG_M:                         commands.ViGotoScreenMiddle(),
        seqs.BIG_N:                         commands.ViRepeatSearchBackward(),
        seqs.BIG_O:                         commands.ViInsertLineBefore(),
        seqs.BIG_P:                         commands.ViPasteBefore(),
        seqs.BIG_R:                         commands.ViEnterReplaceMode(),
        seqs.BIG_S:                         commands.ViSubstituteByLines(),
        seqs.BIG_T:                         commands.ViSearchCharBackward(),
        seqs.BIG_V:                         commands.ViEnterVisualLineMode(),
        seqs.BIG_W:                         commands.ViMoveByBigWords(),
        seqs.BIG_X:                         commands.ViLeftDeleteChar(),
        seqs.BIG_Y:                         commands.ViCopyLine(),
        seqs.BIG_Z:                         commands.ViOpenNameSpace(),
        seqs.BIG_Z_BIG_Q:                   commands.ViExitEditor(),
        seqs.BIG_Z_BIG_Z:                   commands.ViCloseFile(),
        seqs.C:                             commands.ViChangeByChars(),
        seqs.CC:                            commands.ViChangeLine(),
        seqs.COLON:                         commands.ViEnterCommandLineMode(),
        seqs.COMMA:                         commands.ViRepeatCharSearchBackward(),
        seqs.CTRL_A:                        commands.ViAddToNumber(),
        seqs.CTRL_B:                        commands.ViMoveScreenUp(),
        seqs.CTRL_BIG_F:                    commands.StFinInFiles(),
        seqs.CTRL_BIG_P:                    commands.StShowCommandPalette(),
        seqs.CTRL_D:                        commands.ViMoveHalfScreenDown(),
        seqs.CTRL_E:                        commands.ViScrollByLinesUp(),
        seqs.CTRL_F:                        commands.ViMoveScreenDown(),
        seqs.CTRL_G:                        commands.ViShowFileStatus(),
        seqs.CTRL_K:                        commands.ViOpenNameSpace(),
        seqs.CTRL_K_CTRL_B:                 commands.StToggleSidebar(),
        seqs.CTRL_P:                        commands.StShowGotoAnything(),
        seqs.CTRL_R:                        commands.ViRedo(),
        seqs.CTRL_U:                        commands.ViMoveHalfScreenUp(),
        seqs.CTRL_V:                        commands.ViEnterVisualBlockMode(),
        seqs.CTRL_W:                        commands.ViOpenNameSpace(),
        seqs.CTRL_W_BIG_H:                  commands.ViSendViewToLeftPane(),
        seqs.CTRL_W_BIG_L:                  commands.ViSendViewToRightPane(),
        seqs.CTRL_W_H:                      commands.ViActivatePaneToTheLeft(),
        seqs.CTRL_W_L:                      commands.ViActivatePaneToTheRight(),
        seqs.CTRL_W_Q:                      commands.ViDestroyCurrentPane(),
        seqs.CTRL_W_V:                      commands.ViSplitVertically(),
        seqs.CTRL_X:                        commands.ViSubtractFromNumber(),
        seqs.CTRL_Y:                        commands.ViScrollByLinesDown(),
        seqs.D:                             commands.ViDeleteByChars(),
        seqs.DD:                            commands.ViDeleteLine(),
        seqs.DOLLAR:                        commands.ViMoveToEol(),
        seqs.DOT:                           commands.ViRepeat(),
        seqs.DOUBLE_QUOTE:                  commands.ViOpenRegister(),
        seqs.DOWN:                          commands.ViMoveDownByLines(),
        seqs.E:                             commands.ViMoveByWordEnds(),
        seqs.END:                           commands.ViMoveToEol(),
        seqs.ENTER:                         commands.ViMotionEnter(),
        seqs.EQUAL:                         commands.ViReindent(),
        seqs.EQUAL_EQUAL:                   commands.ViReindentLine(),
        seqs.ESC:                           commands.ViEnterNormalMode(),
        seqs.F11:                           commands.StToggleFullScreen(),
        seqs.CTRL_F2:                       commands.StToggleBookmark(),
        seqs.CTRL_F12:                      commands.StGotoSymbolInFile(),
        seqs.F12:                           commands.StGotoDefinition(),
        seqs.F2:                            commands.StNextBookmark(),
        seqs.CTRL_SHIFT_F2:                 commands.StClearBookmarks(),
        seqs.F3:                            commands.StFindNext(),
        # seqs.CTRL_R_EQUAL:              cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.F4:                            commands.StFindNextResult(),
        seqs.F6:                            commands.StToggleSpelling(),
        seqs.F7:                            commands.StBuild(),
        seqs.F:                             commands.ViSearchCharForward(inclusive=True),
        seqs.G:                             commands.ViOpenNameSpace(),
        seqs.G_BIG_D:                       commands.ViGotoSymbolInProject(),
        seqs.G_BIG_H:                       commands.ViEnterSelectModeForSearch(),
        seqs.G_BIG_J:                       commands.ViJoinLinesNoSeparator(),
        seqs.G_BIG_T:                       commands.ViActivatePreviousTab(),
        seqs.G_BIG_U:                       commands.ViChangeToUpperCaseByChars(),
        seqs.G_BIG_U_BIG_U:                 commands.ViChangeToUpperCaseByLines(),
        seqs.G_BIG_U_G_BIG_U:               commands.ViChangeToUpperCaseByLines(),
        seqs.G_TILDE:                       commands.ViInvertCaseByChars(),
        seqs.G_TILDE_G_TILDE:               commands.ViInvertCaseByLines(),
        seqs.G_TILDE_TILDE:                 commands.ViInvertCaseByLines(),
        seqs.G_UNDERSCORE:                  commands.ViMoveToSoftEol(),
        seqs.GD:                            commands.ViGotoSymbolInFile(),
        seqs.GE:                            commands.ViMoveByWordEndsBackward(),
        seqs.GG:                            commands.ViGotoBof(),
        seqs.GH:                            commands.ViEnterSelectMode(),
        seqs.GJ:                            commands.ViMoveByScreenLineDown(),
        seqs.GK:                            commands.ViMoveByScreenLineUp,
        seqs.GQ:                            commands.ViReformat(),
        seqs.GREATER_THAN:                  commands.ViIndent(),
        seqs.GREATER_THAN_GREATER_THAN:     commands.ViIndentLine(),
        seqs.GT:                            commands.ViActivateNextTab(),
        seqs.GU:                            commands.ViChangeToLowerCaseByChars(),
        seqs.GUGU:                          commands.ViChangeToLowerCaseByLines(),
        seqs.GUU:                           commands.ViChangeToLowerCaseByLines(),
        seqs.GV:                            commands.ViRestoreVisualSelections(),
        seqs.H:                             commands.ViMoveLeftByChars(),
        seqs.HAT:                           commands.ViMoveToBol(),
        seqs.HOME:                          commands.ViMoveToBol(),
        # seqs.QUOTE_QUOTE:                 cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        # seqs.RIGHT_SQUARE_BRACKET:        cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.LEFT:                          commands.ViMoveLeftByChars(),
        seqs.RIGHT:                         commands.ViMoveRightByChars(),
        seqs.I:                             commands.ViEnterInserMode(),
        seqs.J:                             commands.ViMoveDownByLines(),
        seqs.K:                             commands.ViMoveUpByLines(),
        seqs.L:                             commands.ViMoveRightByChars(),
        seqs.LEFT_BRACE:                    commands.ViMoveByBlockUp(),
        seqs.LEFT_PAREN:                    commands.ViMoveBySentenceUp(),
        seqs.LEFT_SQUARE_BRACKET:           commands.ViMoveBySquareBracketUp(),
        seqs.LESS_THAN:                     commands.ViUnindent(),
        seqs.LESS_THAN_LESS_THAN:           commands.ViUnindentLine(),
        seqs.M:                             commands.ViSetMark(),
        seqs.N:                             commands.ViRepeatSearchForward(),
        seqs.O:                             commands.ViInsertLineAfter(),
        seqs.OCTOTHORP:                     commands.ViReverseFindWord(),
        seqs.P:                             commands.ViPasteAfter(),
        seqs.PERCENT:                       commands.ViGotoLinesPercent(),
        seqs.PIPE:                          commands.ViMoveByLineCols(),
        seqs.Q:                             commands.ViToggleMacroRecorder(),
        seqs.QUESTION_MARK:                 commands.ViSearchBackward(),
        seqs.QUOTE:                         commands.ViGotoMark(),
        seqs.R:                             commands.ViReplaceCharacters(),
        seqs.RIGHT_BRACE:                   commands.ViMoveByBlockDown(),
        seqs.RIGHT_PAREN:                   commands.ViMoveBySentenceDown(),
        seqs.S:                             commands.ViSubstituteChar(),
        seqs.SEMICOLON:                     commands.ViRepeatCharSearchForward(),
        seqs.SHIFT_ENTER:                   commands.ViShiftEnterMotion(),
        seqs.SLASH:                         commands.ViSearchForward(),
        seqs.SHIFT_CTRL_F12:                commands.StGotoSymbolInProject(),
        seqs.SHIFT_F2:                      commands.StPrevBookmark(),
        seqs.SHIFT_F3:                      commands.StFindPrev(),
        seqs.SHIFT_F4:                      commands.StFindPrevResult(),
        seqs.UP:                            commands.ViMoveUpByLines(),
        seqs.Z:                             commands.ViOpenNameSpace(),
        seqs.SPACE:                         commands.ViMoveRightByChars(),
        seqs.STAR:                          commands.ViFindWord(),
        seqs.T:                             commands.ViSearchCharForward(),
        seqs.TILDE:                         commands.ViForceInvertCaseByChars(),
        seqs.U:                             commands.ViUndo(),
        seqs.UNDERSCORE:                    commands.ViMoveToBol(),
        seqs.V:                             commands.ViEnterVisualMode(),
        seqs.W:                             commands.ViMoveByWords(),
        seqs.X:                             commands.ViRightDeleteChars(),
        seqs.Y:                             commands.ViYankByChars(),
        seqs.YY:                            commands.ViYankLine(),
        seqs.Z_ENTER:                       commands.ViScrollToScreenTop(),
        seqs.Z_MINUS:                       commands.ViScrollToScreenBottom(),
        seqs.ZB:                            commands.ViScrollToScreenBottom(),
        seqs.ZERO:                          commands.ViMoveToHardBol(),
        seqs.ZT:                            commands.ViScrollToScreenTop(),
        seqs.ZZ:                            commands.ViScrollToScreenCenter(),
    },

    # Visual Mode ============================================================
    # XXX: We probably don't need to define all of these; select those that
    #      are actually legal visual mode key sequences.

    modes.VISUAL: {
        seqs.B:                             commands.ViMoveByWordsBackward(),
        seqs.A:                             commands.ViATextObject(),
        seqs.BIG_A:                         commands.ViInsertAtEol(),
        seqs.BIG_B:                         commands.ViMoveByBigWordsBackward(),
        seqs.BIG_C:                         commands.ViChangeToEol(),
        seqs.BIG_D:                         commands.ViDeleteToEol(),
        seqs.BIG_E:                         commands.ViMoveByBigWordEnds(),
        seqs.BIG_F:                         commands.ViSearchCharBackward(inclusive=True),
        seqs.BIG_G:                         commands.ViGotoEof(),
        seqs.BIG_H:                         commands.ViGotoScreenTop(),
        seqs.BIG_I:                         commands.ViITextObject(),
        seqs.BIG_J:                         commands.ViJoinLines(),
        seqs.ALT_CTRL_P:                    commands.StShowSwitchProject(),
        seqs.AT:                            commands.ViOpenMacrosForRepeating(),
        seqs.BACKTICK:                      commands.ViGotoExactMarkXpos(),
        seqs.BIG_L:                         commands.ViGotoScreenBottom(),
        seqs.BIG_M:                         commands.ViGotoScreenMiddle(),
        seqs.BIG_N:                         commands.ViRepeatSearchBackward(),
        seqs.BIG_O:                         commands.ViInsertLineBefore(),
        seqs.BIG_P:                         commands.ViPasteBefore(),
        seqs.BIG_R:                         commands.ViEnterReplaceMode(),
        seqs.BIG_S:                         commands.ViSubstituteByLines(),
        seqs.BIG_T:                         commands.ViSearchCharBackward(),
        seqs.BIG_U:                         commands.ViChangeToUpperCaseByChars(),
        seqs.BIG_V:                         commands.ViEnterVisualLineMode(),
        seqs.BIG_W:                         commands.ViMoveByBigWords(),
        seqs.BIG_X:                         commands.ViLeftDeleteChar(),
        seqs.BIG_Y:                         commands.ViCopyLine(),
        seqs.BIG_Z:                         commands.ViOpenNameSpace(),
        seqs.BIG_Z_BIG_Q:                   commands.ViExitEditor(),
        seqs.BIG_Z_BIG_Z:                   commands.ViCloseFile(),
        seqs.C:                             commands.ViChangeByChars(),
        seqs.CC:                            commands.ViChangeLine(),
        seqs.COLON:                         commands.ViEnterCommandLineMode(),
        seqs.COMMA:                         commands.ViRepeatCharSearchBackward(),
        seqs.CTRL_A:                        commands.ViAddToNumber(),
        seqs.CTRL_B:                        commands.ViMoveScreenUp(),
        seqs.CTRL_BIG_F:                    commands.StFinInFiles(),
        seqs.CTRL_BIG_P:                    commands.StShowCommandPalette(),
        seqs.CTRL_D:                        commands.ViMoveHalfScreenDown(),
        seqs.CTRL_E:                        commands.ViScrollByLinesUp(),
        seqs.CTRL_F:                        commands.ViMoveScreenDown(),
        seqs.CTRL_G:                        commands.ViShowFileStatus(),
        seqs.CTRL_K:                        commands.ViOpenNameSpace(),
        seqs.CTRL_K_CTRL_B:                 commands.StToggleSidebar(),
        seqs.CTRL_P:                        commands.StShowGotoAnything(),
        seqs.CTRL_R:                        commands.ViRedo(),
        seqs.CTRL_U:                        commands.ViMoveHalfScreenUp(),
        seqs.CTRL_V:                        commands.ViEnterVisualBlockMode(),
        seqs.CTRL_W:                        commands.ViOpenNameSpace(),
        seqs.CTRL_W_BIG_H:                  commands.ViSendViewToLeftPane(),
        seqs.CTRL_W_BIG_L:                  commands.ViSendViewToRightPane(),
        seqs.CTRL_W_H:                      commands.ViActivatePaneToTheLeft(),
        seqs.CTRL_W_L:                      commands.ViActivatePaneToTheRight(),
        seqs.CTRL_W_Q:                      commands.ViDestroyCurrentPane(),
        seqs.CTRL_W_V:                      commands.ViSplitVertically(),
        seqs.CTRL_X:                        commands.ViSubtractFromNumber(),
        seqs.CTRL_Y:                        commands.ViScrollByLinesDown(),
        seqs.D:                             commands.ViDeleteByChars(),
        seqs.DD:                            commands.ViDeleteLine(),
        seqs.DOLLAR:                        commands.ViMoveToEol(),
        seqs.DOT:                           commands.ViRepeat(),
        seqs.DOUBLE_QUOTE:                  commands.ViOpenRegister(),
        seqs.DOWN:                          commands.ViMoveDownByLines(),
        seqs.E:                             commands.ViMoveByWordEnds(),
        seqs.END:                           commands.ViMoveToEol(),
        seqs.ENTER:                         commands.ViMotionEnter(),
        seqs.EQUAL:                         commands.ViReindent(),
        seqs.EQUAL_EQUAL:                   commands.ViReindentLine(),
        seqs.ESC:                           commands.ViEnterNormalMode(),
        seqs.F11:                           commands.StToggleFullScreen(),
        seqs.CTRL_F2:                       commands.StToggleBookmark(),
        seqs.CTRL_F12:                      commands.StGotoSymbolInFile(),
        seqs.F12:                           commands.StGotoDefinition(),
        seqs.F2:                            commands.StNextBookmark(),
        seqs.CTRL_SHIFT_F2:                 commands.StClearBookmarks(),
        seqs.F3:                            commands.StFindNext(),
        # seqs.CTRL_R_EQUAL:              cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.F4:                            commands.StFindNextResult(),
        seqs.F6:                            commands.StToggleSpelling(),
        seqs.F7:                            commands.StBuild(),
        seqs.F:                             commands.ViSearchCharForward(inclusive=True),
        seqs.G:                             commands.ViOpenNameSpace(),
        seqs.G_BIG_D:                       commands.ViGotoSymbolInProject(),
        seqs.G_BIG_H:                       commands.ViEnterSelectModeForSearch(),
        seqs.G_BIG_J:                       commands.ViJoinLinesNoSeparator(),
        seqs.G_BIG_T:                       commands.ViActivatePreviousTab(),
        seqs.G_BIG_U:                       commands.ViChangeToLowerCaseByChars(),
        seqs.G_BIG_U_BIG_U:                 commands.ViChangeToUpperCaseByLines(),
        seqs.G_BIG_U_G_BIG_U:               commands.ViChangeToUpperCaseByLines(),
        seqs.G_TILDE:                       commands.ViInvertCaseByChars(),
        seqs.G_TILDE_G_TILDE:               commands.ViInvertCaseByLines(),
        seqs.G_TILDE_TILDE:                 commands.ViInvertCaseByLines(),
        seqs.G_UNDERSCORE:                  commands.ViMoveToSoftEol(),
        seqs.GD:                            commands.ViGotoSymbolInFile(),
        seqs.GE:                            commands.ViMoveByWordEndsBackward(),
        seqs.GG:                            commands.ViGotoBof(),
        seqs.GH:                            commands.ViEnterSelectMode(),
        seqs.GJ:                            commands.ViMoveByScreenLineDown(),
        seqs.GK:                            commands.ViMoveByScreenLineUp,
        seqs.GQ:                            commands.ViReformat(),
        seqs.GREATER_THAN:                  commands.ViIndent(),
        seqs.GREATER_THAN_GREATER_THAN:     commands.ViIndentLine(),
        seqs.GT:                            commands.ViActivateNextTab(),
        seqs.GU:                            commands.ViChangeToLowerCaseByChars(),
        seqs.GUGU:                          commands.ViChangeToLowerCaseByLines(),
        seqs.GUU:                           commands.ViChangeToLowerCaseByLines(),
        seqs.GV:                            commands.ViRestoreVisualSelections(),
        seqs.H:                             commands.ViMoveLeftByChars(),
        seqs.HAT:                           commands.ViMoveToBol(),
        seqs.HOME:                          commands.ViMoveToBol(),
        # seqs.QUOTE_QUOTE:                 cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        # seqs.RIGHT_SQUARE_BRACKET:        cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.LEFT:                          commands.ViMoveLeftByChars(),
        seqs.RIGHT:                         commands.ViMoveRightByChars(),
        seqs.I:                             commands.ViITextObject(),
        seqs.J:                             commands.ViMoveDownByLines(),
        seqs.K:                             commands.ViMoveUpByLines(),
        seqs.L:                             commands.ViMoveRightByChars(),
        seqs.LEFT_BRACE:                    commands.ViMoveByBlockUp(),
        seqs.LEFT_PAREN:                    commands.ViMoveBySentenceUp(),
        seqs.LEFT_SQUARE_BRACKET:           commands.ViMoveBySquareBracketUp(),
        seqs.LESS_THAN:                     commands.ViUnindent(),
        seqs.LESS_THAN_LESS_THAN:           commands.ViUnindentLine(),
        seqs.M:                             commands.ViSetMark(),
        seqs.N:                             commands.ViRepeatSearchForward(),
        seqs.O:                             commands.ViInsertLineAfter(),
        seqs.OCTOTHORP:                     commands.ViReverseFindWord(),
        seqs.P:                             commands.ViPasteAfter(),
        seqs.PERCENT:                       commands.ViGotoLinesPercent(),
        seqs.PIPE:                          commands.ViMoveByLineCols(),
        seqs.Q:                             commands.ViToggleMacroRecorder(),
        seqs.QUESTION_MARK:                 commands.ViSearchBackward(),
        seqs.QUOTE:                         commands.ViGotoMark(),
        seqs.R:                             commands.ViReplaceCharacters(),
        seqs.RIGHT_BRACE:                   commands.ViMoveByBlockDown(),
        seqs.RIGHT_PAREN:                   commands.ViMoveBySentenceDown(),
        seqs.S:                             commands.ViSubstituteChar(),
        seqs.SEMICOLON:                     commands.ViRepeatCharSearchForward(),
        seqs.SHIFT_ENTER:                   commands.ViShiftEnterMotion(),
        seqs.SLASH:                         commands.ViSearchForward(),
        seqs.SHIFT_CTRL_F12:                commands.StGotoSymbolInProject(),
        seqs.SHIFT_F2:                      commands.StPrevBookmark(),
        seqs.SHIFT_F3:                      commands.StFindPrev(),
        seqs.SHIFT_F4:                      commands.StFindPrevResult(),
        seqs.UP:                            commands.ViMoveUpByLines(),
        seqs.Z:                             commands.ViOpenNameSpace(),
        seqs.SPACE:                         commands.ViMoveRightByChars(),
        seqs.STAR:                          commands.ViFindWord(),
        seqs.T:                             commands.ViSearchCharForward(),
        seqs.TILDE:                         commands.ViInvertCaseByChars(),
        seqs.U:                             commands.ViChangeToLowerCaseByChars(),
        seqs.UNDERSCORE:                    commands.ViMoveToBol(),
        seqs.V:                             commands.ViEnterVisualMode(),
        seqs.W:                             commands.ViMoveByWords(),
        seqs.X:                             commands.ViRightDeleteChars(),
        seqs.Y:                             commands.ViYankByChars(),
        seqs.YY:                            commands.ViYankLine(),
        seqs.Z_ENTER:                       commands.ViScrollToScreenTop(),
        seqs.Z_MINUS:                       commands.ViScrollToScreenBottom(),
        seqs.ZB:                            commands.ViScrollToScreenBottom(),
        seqs.ZERO:                          commands.ViMoveToHardBol(),
        seqs.ZT:                            commands.ViScrollToScreenTop(),
        seqs.ZZ:                            commands.ViScrollToScreenCenter(),
    },

    modes.OPERATOR_PENDING: {
        seqs.B:                             commands.ViMoveByWordsBackward(),
        seqs.A:                             commands.ViATextObject(),
        seqs.BIG_B:                         commands.ViMoveByBigWordsBackward(),
        seqs.BIG_E:                         commands.ViMoveByBigWordEnds(),
        seqs.BIG_F:                         commands.ViSearchCharBackward(inclusive=True),
        seqs.BIG_G:                         commands.ViGotoEof(),
        seqs.BIG_H:                         commands.ViGotoScreenTop(),
        seqs.BACKTICK:                      commands.ViGotoExactMarkXpos(),
        seqs.BIG_L:                         commands.ViGotoScreenBottom(),
        seqs.BIG_M:                         commands.ViGotoScreenMiddle(),
        seqs.BIG_N:                         commands.ViRepeatSearchBackward(),
        seqs.BIG_T:                         commands.ViSearchCharBackward(),
        seqs.BIG_W:                         commands.ViMoveByBigWords(),
        seqs.BIG_Z:                         commands.ViOpenNameSpace(),
        seqs.COMMA:                         commands.ViRepeatCharSearchBackward(),
        seqs.CTRL_B:                        commands.ViMoveScreenUp(),
        seqs.CTRL_D:                        commands.ViMoveHalfScreenDown(),
        seqs.CTRL_F:                        commands.ViMoveScreenDown(),
        seqs.CTRL_U:                        commands.ViMoveHalfScreenUp(),
        seqs.DOLLAR:                        commands.ViMoveToEol(),
        seqs.DOWN:                          commands.ViMoveDownByLines(),
        seqs.E:                             commands.ViMoveByWordEnds(),
        seqs.END:                           commands.ViMoveToEol(),
        seqs.ENTER:                         commands.ViMotionEnter(),
        seqs.ESC:                           commands.ViEnterNormalMode(),
        seqs.F:                             commands.ViSearchCharForward(inclusive=True),
        seqs.G:                             commands.ViOpenNameSpace(),
        seqs.G_UNDERSCORE:                  commands.ViMoveToSoftEol(),
        seqs.GD:                            commands.ViGotoSymbolInFile(),
        seqs.GE:                            commands.ViMoveByWordEndsBackward(),
        seqs.GG:                            commands.ViGotoBof(),
        seqs.GJ:                            commands.ViMoveByScreenLineDown(),
        seqs.GK:                            commands.ViMoveByScreenLineUp,
        seqs.H:                             commands.ViMoveLeftByChars(),
        seqs.HAT:                           commands.ViMoveToBol(),
        seqs.HOME:                          commands.ViMoveToBol(),
        # seqs.QUOTE_QUOTE:                 cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        # seqs.RIGHT_SQUARE_BRACKET:        cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.LEFT:                          commands.ViMoveLeftByChars(),
        seqs.RIGHT:                         commands.ViMoveRightByChars(),
        seqs.I:                             commands.ViITextObject(),
        seqs.J:                             commands.ViMoveDownByLines(),
        seqs.K:                             commands.ViMoveUpByLines(),
        seqs.L:                             commands.ViMoveRightByChars(),
        seqs.LEFT_BRACE:                    commands.ViMoveByBlockUp(),
        seqs.LEFT_PAREN:                    commands.ViMoveBySentenceUp(),
        seqs.LEFT_SQUARE_BRACKET:           commands.ViMoveBySquareBracketUp(),
        seqs.LESS_THAN:                     commands.ViUnindent(),
        seqs.N:                             commands.ViRepeatSearchForward(),
        seqs.OCTOTHORP:                     commands.ViReverseFindWord(),
        seqs.PERCENT:                       commands.ViGotoLinesPercent(),
        seqs.PIPE:                          commands.ViMoveByLineCols(),
        seqs.QUESTION_MARK:                 commands.ViSearchBackward(),
        seqs.QUOTE:                         commands.ViGotoMark(),
        seqs.RIGHT_BRACE:                   commands.ViMoveByBlockDown(),
        seqs.RIGHT_PAREN:                   commands.ViMoveBySentenceDown(),
        seqs.SEMICOLON:                     commands.ViRepeatCharSearchForward(),
        seqs.SHIFT_ENTER:                   commands.ViShiftEnterMotion(),
        seqs.SLASH:                         commands.ViSearchForward(),
        seqs.UP:                            commands.ViMoveUpByLines(),
        seqs.Z:                             commands.ViOpenNameSpace(),
        seqs.SPACE:                         commands.ViMoveRightByChars(),
        seqs.STAR:                          commands.ViFindWord(),
        seqs.T:                             commands.ViSearchCharForward(),
        seqs.TILDE:                         commands.ViInvertCaseByChars(),
        seqs.UNDERSCORE:                    commands.ViMoveToBol(),
        seqs.W:                             commands.ViMoveByWords(),
        seqs.ZERO:                          commands.ViMoveToHardBol(),
    },

    # Visual Line Mode =======================================================

    modes.VISUAL_LINE: {
        seqs.BIG_A:                         commands.ViInsertAtEol(),
        seqs.BIG_C:                         commands.ViChangeToEol(),
        seqs.BIG_D:                         commands.ViDeleteToEol(),
        seqs.BIG_G:                         commands.ViGotoEof(),
        seqs.BIG_H:                         commands.ViGotoScreenTop(),
        seqs.BIG_I:                         commands.ViInsertAtBol(),
        seqs.BIG_J:                         commands.ViJoinLines(),
        seqs.ALT_CTRL_P:                    commands.StShowSwitchProject(),
        seqs.AT:                            commands.ViOpenMacrosForRepeating(),
        seqs.BIG_L:                         commands.ViGotoScreenBottom(),
        seqs.BIG_M:                         commands.ViGotoScreenMiddle(),
        seqs.BIG_N:                         commands.ViRepeatSearchBackward(),
        seqs.BIG_O:                         commands.ViInsertLineBefore(),
        seqs.BIG_P:                         commands.ViPasteBefore(),
        seqs.BIG_S:                         commands.ViSubstituteByLines(),
        seqs.BIG_U:                         commands.ViChangeToUpperCaseByChars(),
        seqs.BIG_V:                         commands.ViEnterVisualLineMode(),
        seqs.BIG_X:                         commands.ViLeftDeleteChar(),
        seqs.BIG_Y:                         commands.ViCopyLine(),
        seqs.BIG_Z:                         commands.ViOpenNameSpace(),
        seqs.C:                             commands.ViChangeByChars(),
        seqs.COLON:                         commands.ViEnterCommandLineMode(),
        seqs.CTRL_B:                        commands.ViMoveScreenUp(),
        seqs.CTRL_BIG_P:                    commands.StShowCommandPalette(),
        seqs.CTRL_D:                        commands.ViMoveHalfScreenDown(),
        seqs.CTRL_E:                        commands.ViScrollByLinesUp(),
        seqs.CTRL_F:                        commands.ViMoveScreenDown(),
        seqs.CTRL_K:                        commands.ViOpenNameSpace(),
        seqs.CTRL_K_CTRL_B:                 commands.StToggleSidebar(),
        seqs.CTRL_P:                        commands.StShowGotoAnything(),
        seqs.CTRL_R:                        commands.ViRedo(),
        seqs.CTRL_U:                        commands.ViMoveHalfScreenUp(),
        seqs.CTRL_Y:                        commands.ViScrollByLinesDown(),
        seqs.D:                             commands.ViDeleteByChars(),
        seqs.DOT:                           commands.ViRepeat(),
        seqs.DOUBLE_QUOTE:                  commands.ViOpenRegister(),
        seqs.DOWN:                          commands.ViMoveDownByLines(),
        seqs.E:                             commands.ViMoveByWordEnds(),
        seqs.ENTER:                         commands.ViMotionEnter(),
        seqs.EQUAL:                         commands.ViReindent(),
        seqs.ESC:                           commands.ViEnterNormalMode(),
        seqs.F11:                           commands.StToggleFullScreen(),
        seqs.CTRL_F2:                       commands.StToggleBookmark(),
        # seqs.CTRL_R_EQUAL:              cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.F6:                            commands.StToggleSpelling(),
        seqs.F7:                            commands.StBuild(),
        seqs.G:                             commands.ViOpenNameSpace(),
        seqs.G_BIG_D:                       commands.ViGotoSymbolInProject(),
        seqs.G_BIG_J:                       commands.ViJoinLinesNoSeparator(),
        seqs.G_BIG_U:                       commands.ViChangeToLowerCaseByChars(),
        seqs.G_TILDE:                       commands.ViInvertCaseByChars(),
        seqs.G_UNDERSCORE:                  commands.ViMoveToSoftEol(),
        seqs.GD:                            commands.ViGotoSymbolInFile(),
        seqs.GE:                            commands.ViMoveByWordEndsBackward(),
        seqs.GG:                            commands.ViGotoBof(),
        seqs.GQ:                            commands.ViReformat(),
        seqs.GREATER_THAN:                  commands.ViIndent(),
        seqs.GT:                            commands.ViActivateNextTab(),
        seqs.GU:                            commands.ViChangeToLowerCaseByLines(),
        seqs.H:                             commands.ViMoveLeftByChars(),
        seqs.HAT:                           commands.ViMoveToBol(),
        seqs.HOME:                          commands.ViMoveToBol(),
        # seqs.QUOTE_QUOTE:                 cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        # seqs.RIGHT_SQUARE_BRACKET:        cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.LEFT:                          commands.ViMoveLeftByChars(),
        seqs.RIGHT:                         commands.ViMoveRightByChars(),
        seqs.J:                             commands.ViMoveDownByLines(),
        seqs.K:                             commands.ViMoveUpByLines(),
        seqs.L:                             commands.ViMoveRightByChars(),
        seqs.LEFT_BRACE:                    commands.ViMoveByBlockUp(),
        seqs.LEFT_PAREN:                    commands.ViMoveBySentenceUp(),
        seqs.LEFT_SQUARE_BRACKET:           commands.ViMoveBySquareBracketUp(),
        seqs.LESS_THAN:                     commands.ViUnindent(),
        seqs.N:                             commands.ViRepeatSearchForward(),
        seqs.O:                             commands.ViInsertLineAfter(),
        seqs.OCTOTHORP:                     commands.ViReverseFindWord(),
        seqs.P:                             commands.ViPasteAfter(),
        seqs.PERCENT:                       commands.ViGotoLinesPercent(),
        seqs.Q:                             commands.ViToggleMacroRecorder(),
        seqs.QUESTION_MARK:                 commands.ViSearchBackward(),
        seqs.QUOTE:                         commands.ViGotoMark(),
        seqs.R:                             commands.ViReplaceCharacters(),
        seqs.RIGHT_BRACE:                   commands.ViMoveByBlockDown(),
        seqs.RIGHT_PAREN:                   commands.ViMoveBySentenceDown(),
        seqs.S:                             commands.ViSubstituteChar(),
        seqs.SEMICOLON:                     commands.ViRepeatCharSearchForward(),
        seqs.SHIFT_ENTER:                   commands.ViShiftEnterMotion(),
        seqs.SLASH:                         commands.ViSearchForward(),
        seqs.U:                             commands.ViChangeToLowerCaseByChars(),
        seqs.UP:                            commands.ViMoveUpByLines(),
        seqs.Z:                             commands.ViOpenNameSpace(),
        seqs.TILDE:                         commands.ViInvertCaseByChars(),
        seqs.U:                             commands.ViUndo(),
        seqs.UNDERSCORE:                    commands.ViMoveToBol(),
        seqs.V:                             commands.ViEnterVisualMode(),
        seqs.W:                             commands.ViMoveByWords(),
        seqs.X:                             commands.ViRightDeleteChars(),
        seqs.Y:                             commands.ViYankByChars(),
        seqs.Z_ENTER:                       commands.ViScrollToScreenTop(),
        seqs.Z_MINUS:                       commands.ViScrollToScreenBottom(),
        seqs.ZB:                            commands.ViScrollToScreenBottom(),
        seqs.ZERO:                          commands.ViMoveToHardBol(),
        seqs.ZT:                            commands.ViScrollToScreenTop(),
        seqs.ZZ:                            commands.ViScrollToScreenCenter(),
    },

    # Mode Visual Block ======================================================

    modes.VISUAL_BLOCK: {
        seqs.B:                             commands.ViMoveByWordsBackward(),
        seqs.A:                             commands.ViATextObject(),
        seqs.BIG_A:                         commands.ViInsertAtEol(),
        seqs.BIG_B:                         commands.ViMoveByBigWordsBackward(),
        seqs.BIG_C:                         commands.ViChangeToEol(),
        seqs.BIG_D:                         commands.ViDeleteToEol(),
        seqs.BIG_E:                         commands.ViMoveByBigWordEnds(),
        seqs.BIG_F:                         commands.ViSearchCharBackward(inclusive=True),
        seqs.BIG_G:                         commands.ViGotoEof(),
        seqs.BIG_H:                         commands.ViGotoScreenTop(),
        seqs.BIG_I:                         commands.ViInsertAtBol(),
        seqs.BIG_J:                         commands.ViJoinLines(),
        seqs.ALT_CTRL_P:                    commands.StShowSwitchProject(),
        seqs.AT:                            commands.ViOpenMacrosForRepeating(),
        seqs.BACKTICK:                      commands.ViGotoExactMarkXpos(),
        seqs.BIG_L:                         commands.ViGotoScreenBottom(),
        seqs.BIG_M:                         commands.ViGotoScreenMiddle(),
        seqs.BIG_N:                         commands.ViRepeatSearchBackward(),
        seqs.BIG_O:                         commands.ViInsertLineBefore(),
        seqs.BIG_P:                         commands.ViPasteBefore(),
        seqs.BIG_R:                         commands.ViEnterReplaceMode(),
        seqs.BIG_U:                         commands.ViChangeToUpperCaseByChars(),
        seqs.BIG_T:                         commands.ViSearchCharBackward(),
        seqs.BIG_U:                         commands.ViChangeToUpperCaseByChars(),
        seqs.BIG_V:                         commands.ViEnterVisualLineMode(),
        seqs.BIG_W:                         commands.ViMoveByBigWords(),
        seqs.BIG_X:                         commands.ViLeftDeleteChar(),
        seqs.BIG_Y:                         commands.ViCopyLine(),
        seqs.BIG_Z:                         commands.ViOpenNameSpace(),
        seqs.BIG_Z_BIG_Q:                   commands.ViExitEditor(),
        seqs.BIG_Z_BIG_Z:                   commands.ViCloseFile(),
        seqs.C:                             commands.ViChangeByChars(),
        seqs.CC:                            commands.ViChangeLine(),
        seqs.COLON:                         commands.ViEnterCommandLineMode(),
        seqs.COMMA:                         commands.ViRepeatCharSearchBackward(),
        seqs.CTRL_A:                        commands.ViAddToNumber(),
        seqs.CTRL_B:                        commands.ViMoveScreenUp(),
        seqs.CTRL_BIG_F:                    commands.StFinInFiles(),
        seqs.CTRL_BIG_P:                    commands.StShowCommandPalette(),
        seqs.CTRL_D:                        commands.ViMoveHalfScreenDown(),
        seqs.CTRL_E:                        commands.ViScrollByLinesUp(),
        seqs.CTRL_F:                        commands.ViMoveScreenDown(),
        seqs.CTRL_G:                        commands.ViShowFileStatus(),
        seqs.CTRL_K:                        commands.ViOpenNameSpace(),
        seqs.CTRL_K_CTRL_B:                 commands.StToggleSidebar(),
        seqs.CTRL_P:                        commands.StShowGotoAnything(),
        seqs.CTRL_R:                        commands.ViRedo(),
        seqs.CTRL_U:                        commands.ViMoveHalfScreenUp(),
        seqs.CTRL_V:                        commands.ViEnterVisualBlockMode(),
        seqs.CTRL_W:                        commands.ViOpenNameSpace(),
        seqs.CTRL_W_BIG_H:                  commands.ViSendViewToLeftPane(),
        seqs.CTRL_W_BIG_L:                  commands.ViSendViewToRightPane(),
        seqs.CTRL_W_H:                      commands.ViActivatePaneToTheLeft(),
        seqs.CTRL_W_L:                      commands.ViActivatePaneToTheRight(),
        seqs.CTRL_W_Q:                      commands.ViDestroyCurrentPane(),
        seqs.CTRL_W_V:                      commands.ViSplitVertically(),
        seqs.CTRL_X:                        commands.ViSubtractFromNumber(),
        seqs.CTRL_Y:                        commands.ViScrollByLinesDown(),
        seqs.D:                             commands.ViDeleteByChars(),
        seqs.DD:                            commands.ViDeleteLine(),
        seqs.DOLLAR:                        commands.ViMoveToEol(),
        seqs.DOT:                           commands.ViRepeat(),
        seqs.DOUBLE_QUOTE:                  commands.ViOpenRegister(),
        seqs.DOWN:                          commands.ViMoveDownByLines(),
        seqs.E:                             commands.ViMoveByWordEnds(),
        seqs.END:                           commands.ViMoveToEol(),
        seqs.ENTER:                         commands.ViMotionEnter(),
        seqs.EQUAL:                         commands.ViReindent(),
        seqs.EQUAL_EQUAL:                   commands.ViReindentLine(),
        seqs.ESC:                           commands.ViEnterNormalMode(),
        seqs.F11:                           commands.StToggleFullScreen(),
        seqs.CTRL_F2:                       commands.StToggleBookmark(),
        seqs.CTRL_F12:                      commands.StGotoSymbolInFile(),
        seqs.F12:                           commands.StGotoDefinition(),
        seqs.F2:                            commands.StNextBookmark(),
        seqs.CTRL_SHIFT_F2:                 commands.StClearBookmarks(),
        seqs.F3:                            commands.StFindNext(),
        # seqs.CTRL_R_EQUAL:              cmd_defs[modes.NORMAL][cmds.CTRL_R_EQUAL],
        seqs.F4:                            commands.StFindNextResult(),
        seqs.F6:                            commands.StToggleSpelling(),
        seqs.F7:                            commands.StBuild(),
        seqs.F:                             commands.ViSearchCharForward(inclusive=True),
        seqs.G:                             commands.ViOpenNameSpace(),
        seqs.G_BIG_D:                       commands.ViGotoSymbolInProject(),
        seqs.G_BIG_H:                       commands.ViEnterSelectModeForSearch(),
        seqs.G_BIG_J:                       commands.ViJoinLinesNoSeparator(),
        seqs.G_BIG_T:                       commands.ViActivatePreviousTab(),
        seqs.G_BIG_U:                       commands.ViChangeToLowerCaseByChars(),
        seqs.G_BIG_U_BIG_U:                 commands.ViChangeToUpperCaseByLines(),
        seqs.G_BIG_U_G_BIG_U:               commands.ViChangeToUpperCaseByLines(),
        seqs.G_TILDE:                       commands.ViInvertCaseByChars(),
        seqs.G_TILDE_G_TILDE:               commands.ViInvertCaseByLines(),
        seqs.G_TILDE_TILDE:                 commands.ViInvertCaseByLines(),
        seqs.G_UNDERSCORE:                  commands.ViMoveToSoftEol(),
        seqs.GD:                            commands.ViGotoSymbolInFile(),
        seqs.GE:                            commands.ViMoveByWordEndsBackward(),
        seqs.GG:                            commands.ViGotoBof(),
        seqs.GH:                            commands.ViEnterSelectMode(),
        seqs.GJ:                            commands.ViMoveByScreenLineDown(),
        seqs.GK:                            commands.ViMoveByScreenLineUp,
        seqs.GQ:                            commands.ViReformat(),
        seqs.GREATER_THAN:                  commands.ViIndent(),
        seqs.GREATER_THAN_GREATER_THAN:     commands.ViIndentLine(),
        seqs.GT:                            commands.ViActivateNextTab(),
        seqs.GU:                            commands.ViChangeToLowerCaseByLines(),
        seqs.GUGU:                          commands.ViChangeToLowerCaseByLines(),
        seqs.GUU:                           commands.ViChangeToLowerCaseByLines(),
        seqs.GV:                            commands.ViRestoreVisualSelections(),
        seqs.H:                             commands.ViMoveLeftByChars(),
        seqs.HAT:                           commands.ViMoveToBol(),
        seqs.HOME:                          commands.ViMoveToBol(),
        # seqs.QUOTE_QUOTE:                 cmd_defs[modes.NORMAL][cmds.QUOTE_QUOTE],
        # seqs.RIGHT_SQUARE_BRACKET:        cmd_defs[modes.NORMAL][cmds.RIGHT_SQUARE_BRACKET],
        seqs.LEFT:                          commands.ViMoveLeftByChars(),
        seqs.RIGHT:                         commands.ViMoveRightByChars(),
        seqs.I:                             commands.ViITextObject(),
        seqs.J:                             commands.ViMoveDownByLines(),
        seqs.K:                             commands.ViMoveUpByLines(),
        seqs.L:                             commands.ViMoveRightByChars(),
        seqs.LEFT_BRACE:                    commands.ViMoveByBlockUp(),
        seqs.LEFT_PAREN:                    commands.ViMoveBySentenceUp(),
        seqs.LEFT_SQUARE_BRACKET:           commands.ViMoveBySquareBracketUp(),
        seqs.LESS_THAN:                     commands.ViUnindent(),
        seqs.LESS_THAN_LESS_THAN:           commands.ViUnindentLine(),
        seqs.M:                             commands.ViSetMark(),
        seqs.N:                             commands.ViRepeatSearchForward(),
        seqs.O:                             commands.ViInsertLineAfter(),
        seqs.OCTOTHORP:                     commands.ViReverseFindWord(),
        seqs.P:                             commands.ViPasteAfter(),
        seqs.PERCENT:                       commands.ViGotoLinesPercent(),
        seqs.PIPE:                          commands.ViMoveByLineCols(),
        seqs.Q:                             commands.ViToggleMacroRecorder(),
        seqs.QUESTION_MARK:                 commands.ViSearchBackward(),
        seqs.QUOTE:                         commands.ViGotoMark(),
        seqs.R:                             commands.ViReplaceCharacters(),
        seqs.RIGHT_BRACE:                   commands.ViMoveByBlockDown(),
        seqs.RIGHT_PAREN:                   commands.ViMoveBySentenceDown(),
        seqs.S:                             commands.ViSubstituteChar(),
        seqs.SEMICOLON:                     commands.ViRepeatCharSearchForward(),
        seqs.SHIFT_ENTER:                   commands.ViShiftEnterMotion(),
        seqs.SLASH:                         commands.ViSearchForward(),
        seqs.SHIFT_CTRL_F12:                commands.StGotoSymbolInProject(),
        seqs.SHIFT_F2:                      commands.StPrevBookmark(),
        seqs.SHIFT_F3:                      commands.StFindPrev(),
        seqs.SHIFT_F4:                      commands.StFindPrevResult(),
        seqs.UP:                            commands.ViMoveUpByLines(),
        seqs.Z:                             commands.ViOpenNameSpace(),
        seqs.SPACE:                         commands.ViMoveRightByChars(),
        seqs.STAR:                          commands.ViFindWord(),
        seqs.T:                             commands.ViSearchCharForward(),
        seqs.TILDE:                         commands.ViInvertCaseByChars(),
        seqs.U:                             commands.ViChangeToLowerCaseByChars(),
        seqs.UNDERSCORE:                    commands.ViMoveToBol(),
        seqs.V:                             commands.ViEnterVisualMode(),
        seqs.W:                             commands.ViMoveByWords(),
        seqs.X:                             commands.ViRightDeleteChars(),
        seqs.Y:                             commands.ViYankByChars(),
        seqs.YY:                            commands.ViYankLine(),
        seqs.Z_ENTER:                       commands.ViScrollToScreenTop(),
        seqs.Z_MINUS:                       commands.ViScrollToScreenBottom(),
        seqs.ZB:                            commands.ViScrollToScreenBottom(),
        seqs.ZERO:                          commands.ViMoveToHardBol(),
        seqs.ZT:                            commands.ViScrollToScreenTop(),
        seqs.ZZ:                            commands.ViScrollToScreenCenter(),
    },

    # Mode Select ============================================================

    modes.SELECT: {
        # TODO: Better implement the following commands separately.
        seqs.BIG_A: commands.ViInsertAtEol(),
        seqs.BIG_J: commands.ViJoinLines(),
        seqs.I:     commands.ViEnterInserMode(),
        seqs.J:     commands.ViMoveDownByLines(),
        seqs.K:     commands.ViDeselectInstance(),
        seqs.L:     commands.ViMoveRightByChars(),
    },

    # Extra ==================================================================

    '_missing':  dict(name='_missing')
}


# TODO: Add a timeout for ambiguous commands.
# Key sequence to command mapping. Mappings are set by the user.
#
# Returns a partial definition containing the user-pressed keys so that we
# can replay the command exactly as it was typed in.
user_mappings = {
    # 'jkl': dict(name='dd', type=cmd_types.USER),
}


EOF = -2

class key_names:
    """
    Names of special keys.
    """
    BACKSPACE   = '<bs>'
    CR          = '<cr>'
    DOWN        = '<down>'
    END         = '<end>'
    ENTER       = '<enter>'
    ESC         = '<esc>'
    HOME        = '<home>'
    LEFT        = '<left>'
    LESS_THAN   = '<lt>'
    RIGHT       = '<right>'
    SPACE       = '<sp>'
    SPACE_LONG  = '<space>'
    TAB         = '<tab>'
    UP          = '<up>'

    F1          = '<f1>'
    F2          = '<f2>'
    F3          = '<f3>'
    F4          = '<f4>'
    F5          = '<f5>'
    F6          = '<f6>'
    F7          = '<f7>'
    F8          = '<f8>'
    F9          = '<f9>'
    F10         = '<f10>'
    F11         = '<f11>'
    F12         = '<f12>'
    F13         = '<f13>'
    F14         = '<f14>'
    F15         = '<f15>'

    as_list = [
        BACKSPACE,
        CR,
        DOWN,
        END,
        ENTER,
        ESC,
        HOME,
        LEFT,
        LESS_THAN,
        RIGHT,
        SPACE,
        SPACE_LONG,
        TAB,
        UP,

        F1,
        F2,
        F3,
        F4,
        F5,
        F6,
        F7,
        F8,
        F9,
        F10,
        F11,
        F12,
        F13,
        F14,
        F15,
    ]

    max_len = len('<space>')


# TODO: detect counts, registers, marks...
class KeySequenceTokenizer(object):
    """
    Takes in a sequence of key names and tokenizes it.
    """
    def __init__(self, source):
        """
        @source
          A sequence of key names in Vim notation.
        """
        self.idx = -1
        self.source = source
        self.in_named_key = False

    def consume(self):
        self.idx += 1
        if self.idx >= len(self.source):
            self.idx -= -1
            return EOF
        return self.source[self.idx]

    def peek_one(self):
        if (self.idx + 1) >= len(self.source):
            return EOF
        return self.source[self.idx + 1]

    def is_named_key(self, key):
        return key.lower() in key_names.as_list

    def sort_modifiers(self, modifiers):
        """
        Ensures consistency in the order of modifier letters according to:

          c > m > s
        """
        if len(modifiers) == 6:
            modifiers = 'c-m-s-'
        elif len(modifiers) > 2:
            if modifiers.startswith('s-') and modifiers.endswith('c-'):
                modifiers = 'c-s-'
            elif modifiers.startswith('s-') and modifiers.endswith('m-'):
                modifiers = 'm-s-'
            elif modifiers.startswith('m-') and modifiers.endswith('c-'):
                modifiers = 'c-m-'
        return modifiers

    def long_key_name(self):
        self.in_named_key = True
        key_name = ''
        modifiers = ''

        while True:
            c = self.consume()

            if c == EOF:
                raise ValueError("expected '>' at index {0}".format(self.idx))

            elif (c.lower() in ('c', 's', 'm')) and (self.peek_one() == '-'):
                if c.lower() in modifiers.lower():
                    raise ValueError('invalid modifier sequence: {0}'.format(self.source))

                modifiers += c + self.consume()

            elif c == '>' and self.peek_one() == '>':
                modifiers = self.sort_modifiers(modifiers.lower())

                if len(key_name) == 0:
                    return '<' + modifiers.upper() + self.consume() + '>'

                else:
                    raise ValueError('wrong key {0}'.format(key_name))

            elif c == '>':
                modifiers = self.sort_modifiers(modifiers.lower())

                if len(key_name) == 1:
                    if not modifiers:
                        raise ValueError('wrong sequence {0}'.format(self.source))
                    return '<' + modifiers.upper() + key_name + '>'

                elif self.is_named_key('<' + key_name + '>'):
                    self.in_named_key = False
                    return '<' + modifiers.upper() + key_name.lower() + '>'

                else:
                    raise ValueError("'{0}' is not a known key".format(key_name))

            else:
                key_name += c

    def tokenize_one(self):
        c = self.consume()

        if c == '<':
            return self.long_key_name()
        else:
            return c

    def iter_tokenize(self):
        while True:
            token = self.tokenize_one()
            if token == EOF:
                break
            yield token


def to_bare_command_name(seq):
    """
    Strips register and count data from @seq.
    """
    # Special case.
    if seq == '0':
        return seq

    new_seq = re.sub(r'^(?:".)?(?:[1-9]+)?', '', seq)
    # Account for d2d and similar sequences.
    new_seq = list(KeySequenceTokenizer(new_seq).iter_tokenize())

    return ''.join(k for k in new_seq if not k.isdigit())
