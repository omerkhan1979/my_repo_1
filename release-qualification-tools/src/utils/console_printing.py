"""
Module to print text in console in different colors
"""

import sys
import emoji


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def blue(user_input):
    result = bcolors.OKBLUE + bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def cyan(user_input):
    result = bcolors.OKCYAN + bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def green(user_input):
    result = bcolors.OKGREEN + bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def yellow(user_input):
    result = bcolors.WARNING + bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def red(user_input):
    result = bcolors.FAIL + bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def bold(user_input):
    result = bcolors.BOLD + str(user_input) + bcolors.ENDC
    return result


def link(user_input):
    result = bcolors.UNDERLINE + str(user_input) + bcolors.ENDC
    return result


def done(user_input):
    return (
        emoji.emojize(bcolors.BOLD + f":check_mark_button: {user_input}") + bcolors.ENDC
    )


def waiting(user_input):
    return emoji.emojize(bcolors.BOLD + f":stopwatch: {user_input}") + bcolors.ENDC


def error(user_input):
    return emoji.emojize(bcolors.BOLD + f":cross_mark: {user_input}") + bcolors.ENDC


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
