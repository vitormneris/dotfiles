from collections.abc import Callable

import os
import subprocess
from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Output, Screen
from libqtile.lazy import lazy

@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~')
    subprocess.run([home + '/dotfiles/scripts/monitor_xrandr_config.sh'])
    subprocess.Popen(["picom", "--backend", "glx"])
    subprocess.Popen(["dunst"])
    subprocess.Popen(["jesusphrases"])

# Função para pegar o volume atual do microfone
def get_mic_volume():
    try:
        output = subprocess.run(
            ["pactl", "get-source-mute", "@DEFAULT_SOURCE@"],
            capture_output=True, text=True
        ).stdout
        if "yes" in output:
            return "M"
        output = subprocess.run(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"],
            capture_output=True, text=True
        ).stdout
        # Pega o percentual do primeiro canal
        percent = output.split("/")[1].strip()
        return percent
    except:
        return "N/A"

# Função para mutar/desmutar o microfone
def toggle_mic():
    subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])

# Função para aumentar o volume
def increase_mic():
    subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "+5%"])

# Função para diminuir o volume
def decrease_mic():
    subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "-5%"])

# Widget customizado
mic_widget = widget.GenPollText(
    func=get_mic_volume,
    update_interval=1,
    fmt='🎤: {}',
    mouse_callbacks={
        'Button1': toggle_mic,       # Clique esquerdo → mutar
        'Button4': increase_mic,     # Scroll up → aumentar volume
        'Button5': decrease_mic      # Scroll down → diminuir volume
    }
)

# Mover janela para a workspace anterior e ir junto
def window_to_previous_group(qtile):
    if qtile.current_window is not None:
        i = qtile.groups.index(qtile.current_group)
        prev_group = qtile.groups[i - 1].name
        qtile.current_window.togroup(prev_group, switch_group=True)

# Mover janela para a workspace seguinte e ir junto
def window_to_next_group(qtile):
    if qtile.current_window is not None:
        i = qtile.groups.index(qtile.current_group)
        next_group = qtile.groups[(i + 1) % len(qtile.groups)].name
        qtile.current_window.togroup(next_group, switch_group=True)

mod = "mod4"
terminal = "alacritty"

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
    Key(["mod1"], "space", lazy.layout.next(), desc="Move window focus to other window"),

    Key(["mod1"], "Left", lazy.screen.prev_group(), desc="Go to previous group"),
    Key(["mod1"], "Right", lazy.screen.next_group(), desc="Go to next group"),

    Key(["mod1", "shift"], "Left", lazy.function(window_to_previous_group), desc="Move janela para o grupo anterior"),
    Key(["mod1", "shift"], "Right", lazy.function(window_to_next_group), desc="Move janela para o próximo grupo"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "Left", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "Left", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "Down", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "Up", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    Key(["mod1", "control"], "left", lazy.window.resize_floating(-20, 0)),
    Key(["mod1", "control"], "right", lazy.window.resize_floating(20, 0)),
    Key(["mod1", "control"], "down", lazy.window.resize_floating(0, 20)),
    Key(["mod1", "control"], "up", lazy.window.resize_floating(0, -20)),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod],
        "s",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "t", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key(["mod1"], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "space", lazy.spawn("rofi -show drun"), desc="Spawn a command using a prompt widget"),

    Key([], "Print", lazy.spawn("scrot -s -F /home/vitor/Pictures/Screenshots/screenshot-%Y-%m-%d-%H%M%S.png")),

    Key([], "XF86AudioRaiseVolume", lazy.spawn("wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+"), desc="Volume up"),
    Key([], "XF86AudioLowerVolume", lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), desc="Volume down"),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "1234567890"]

# mapeamento: grupo "1" → teclas "1" e "KP_1"
keymap = {
    "1": ["1", "KP_End"],
    "2": ["2", "KP_Down"],
    "3": ["3", "KP_Next"],
    "4": ["4", "KP_Left"],
    "5": ["5", "KP_Begin"],
    "6": ["6", "KP_Right"],
    "7": ["7", "KP_Home"],
    "8": ["8", "KP_Up"],
    "9": ["9", "KP_Prior"],
    "0": ["0", "KP_Insert"],
}

for g in groups:
    for key in keymap[g.name]:
        keys.extend([
            # mod + group number = switch to group
            Key([mod], key, lazy.group[g.name].toscreen(),
                desc=f"Switch to group {g.name}"),
            
            # mod + shift + group number = switch to & move focused window to group
            Key([mod, "shift"], key,
                lazy.window.togroup(g.name, switch_group=True),
                desc=f"Move focused window to group {g.name}"),
                            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ] 
    )    

# Window layout definitions
color1="#d75f5f"
color2="#8f3d3d"
bw=4
mrg=2

layouts = [
    layout.Columns(border_focus_stack=[color1, color2], border_width=bw, margin=mrg, border_on_single=True),
    #layout.Max(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    layout.Stack(num_stacks=1, border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    layout.Bsp(border_focus_stack=[color1, color2], border_width=bw, margin=mrg, border_on_single=True),
    #layout.Matrix(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    layout.MonadTall(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    #layout.MonadWide(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    #layout.RatioTile(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    layout.Tile(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    layout.TreeTab(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    #layout.VerticalTile(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
    #layout.Zoomy(border_focus_stack=[color1, color2], border_width=bw, margin=mrg),
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

# logo = os.path.join(os.path.dirname(libqtile.resources.__file__), "logo.png")
logo = "~/Pictures/Wallpapers/432724.jpg"
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                # NB Systray is incompatible with Wayland, consider using StatusNotifier instead
                # widget.StatusNotifier(),
                widget.Systray(),
                widget.GenPollCommand(
                    cmd='curl -s wttr.in/Sao_Paulo?format=%C+%c+%t',
                    shell=True,
                    update_interval=60,
                    fmt="{}"
                ),              
                widget.Sep(padding=10),
                widget.Memory(fmt='RAM {}', measure_mem='G'),
                widget.CPU(),
                widget.Sep(padding=10),
                widget.GenPollCommand(
                    cmd="bluetoothctl show | awk '/PowerState/ { print toupper($2) }'",
                    fmt="BT: {}",
                    update_interval=2, 
                    shell=True,
                    mouse_callbacks={
                        "Button1": lazy.spawn("alacritty -e bluetoothctl"),
                    },
                ),
                widget.GenPollCommand(
                    cmd="if [[ $(nmcli n connectivity) = full ]]; then echo CONN - $(nmcli device show | awk 'NR <= 6 && /GENERAL.CONNECTION:/ { print $2 }'); else echo DISC; fi",
                    fmt="🌐: {}",
                    update_interval=2, 
                    shell=True,
                    mouse_callbacks={
                        "Button1": lazy.spawn("alacritty -e nmtui"),
                    },
                ),
                widget.Sep(padding=10),
                widget.TextBox("🔉:"),
                # Need to alsa-utils
                widget.PulseVolume(mouse_callbacks={ "Button1": lazy.spawn("pavucontrol") }),
                mic_widget,
                widget.Sep(padding=10),
                widget.TextBox("🔋"),
                widget.Battery(format="{char} {percent:2.0%}", update_interval=5),
                widget.Sep(padding=10),
                widget.Backlight(
                    format="🔆1: {percent:2.0%}",
                    backlight_name="intel_backlight",
                    step=5,
                    mouse_callbacks={
                        "Button4": lazy.spawn("brightnessctl set +5%"),   # Rolagem para cima (aumenta)
                        "Button5": lazy.spawn("brightnessctl set 5%-"),   # Rolagem para baixo (diminui)
                    },
                ),
                widget.GenPollCommand(
                    cmd='ddcutil getvcp 10 | grep -oE "current value =\s*[0-9]+" | awk "{print \$4}"',
                    fmt="🔆2: {}%",
                    update_interval=2, 
                    shell=True,
                    mouse_callbacks={
                        "Button4": lazy.spawn("ddcutil setvcp 10 + 5"),   # Rolagem para cima (aumenta)
                        "Button5": lazy.spawn("ddcutil setvcp 10 - 5"),   # Rolagem para baixo (diminui)
                    },
                ),
                widget.Sep(padding=10),
                widget.Clock(
                    format="%d/%m/%Y %a %H:%M:%S",
                    mouse_callbacks={
                        "Button1": lazy.spawn("korganizer"),   # Rolagem para cima (aumenta)
                    }
                ),
                widget.Sep(padding=10),
                widget.QuickExit(countdown_start=10, default_text="vitor")
            ],
            24,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
        background="#000000",
        wallpaper=logo,
        wallpaper_mode="center",
        # You can uncomment this variable if you see that on X11 floating resize/moving is laggy
        # By default we handle these events delayed to already improve performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
    Screen(
        background="#000000",
        wallpaper=logo,
        wallpaper_mode="center",
    ),
]

# Instead of screens, you can define a function here to specify which Screen
# should correspond to which Output.
fake_screens: list[Screen] | None = None

# Instead of screens or fake screens, you can define a function here that
# returns a list of Screen objects based on the list of Outputs; that way you
# can decide based on e.g. the number of screens, or which ports are plugged
# in exactly what do render in each bar for each screen.
generate_screens: Callable[[list[Output]], list[Screen]] | None = None

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# How long (in seconds) to wait after a screen change event before firing the
# screen_change hook, coalescing bursts of events into a single one.
screen_change_debounce_timeout = 1

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

idle_timers = []  # type: list
idle_inhibitors = []  # type: list

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
