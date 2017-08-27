import os
import sys
from ..utils import warn, py3, BasicSegment

ELLIPSIS = u'\u2026'


def _mode(powerline):
    return powerline.segment_conf("cwd", "mode", "fancy")


def replace_home_dir(cwd):
    home = os.getenv('HOME')
    if cwd.startswith(home):
        return '~' + cwd[len(home):]
    return cwd


def split_path_into_names(cwd):
    names = cwd.split(os.sep)

    if names[0] == '':
        names = names[1:]

    if not names[0]:
        return ['/']

    return names


def requires_special_home_display(powerline, name):
    """Returns true if the given directory name matches the home indicator and
    the chosen theme should use a special home indicator display."""
    return (name == '~' and powerline.theme.HOME_SPECIAL_DISPLAY)


def maybe_shorten_name(powerline, name):
    """If the user has asked for each directory name to be shortened, will
    return the name up to their specified length. Otherwise returns the full
    name."""
    max_size = powerline.segment_conf("cwd", "max_dir_size")
    if max_size:
        return name[:max_size]
    return name


def get_fg_bg(powerline, name, is_last_dir):
    """Returns the foreground and background color to use for the given name.
    """
    if requires_special_home_display(powerline, name):
        return (powerline.theme.HOME_FG, powerline.theme.HOME_BG,)

    if is_last_dir:
        return (powerline.theme.CWD_FG, powerline.theme.PATH_BG,)
    else:
        return (powerline.theme.PATH_FG, powerline.theme.PATH_BG,)


def add_cwd_segment(powerline):
    cwd = powerline.cwd or os.getenv('PWD')
    if not py3:
        cwd = cwd.decode("utf-8")
    cwd = replace_home_dir(cwd)

    if _mode(powerline) == 'plain':
        powerline.append(' %s ' % (cwd,), powerline.theme.CWD_FG, powerline.theme.PATH_BG)
        return

    names = split_path_into_names(cwd)

    max_depth = powerline.segment_conf("cwd", "max_depth", 5)
    if max_depth <= 0:
        warn("Ignoring cwd.max_depth option since it's not greater than 0")
    elif len(names) > max_depth:
        # https://github.com/milkbikis/powerline-shell/issues/148
        # n_before is the number is the number of directories to put before the
        # ellipsis. So if you are at ~/a/b/c/d/e and max depth is 4, it will
        # show `~ a ... d e`.
        #
        # max_depth must be greater than n_before or else you end up repeating
        # parts of the path with the way the splicing is written below.
        n_before = 2 if max_depth > 2 else max_depth - 1
        names = names[:n_before] + [ELLIPSIS] + names[n_before - max_depth:]

    if _mode(powerline) == "dironly":
        # The user has indicated they only want the current directory to be
        # displayed, so chop everything else off
        names = names[-1:]

    for i, name in enumerate(names):
        is_last_dir = (i == len(names) - 1)
        fg, bg = get_fg_bg(powerline, name, is_last_dir)

        separator = powerline.separator_thin
        separator_fg = powerline.theme.SEPARATOR_FG
        if requires_special_home_display(powerline, name) or is_last_dir:
            separator = None
            separator_fg = None

        powerline.append(' %s ' % maybe_shorten_name(powerline, name), fg, bg,
                         separator, separator_fg)


class Segment(BasicSegment):
    def add_to_powerline(self):
        add_cwd_segment(self.powerline)
