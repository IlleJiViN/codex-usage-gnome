import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import GObject from 'gi://GObject';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const UsageIndicator = GObject.registerClass(
class UsageIndicator extends PanelMenu.Button {
    _init(extension) {
        super._init(0.5, 'Codex usage');
        this._extension = extension;
        this._label = new St.Label({text: 'Codex …', y_align: 2});
        this.add_child(this._label);

        const refreshItem = new PopupMenu.PopupMenuItem('Refresh usage', {
            reactive: true,
            can_focus: true,
        });
        refreshItem.connect('activate', () => this.refresh());
        this.menu.addMenuItem(refreshItem);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._details = new PopupMenu.PopupMenuItem('Loading…', {reactive: false});
        this.menu.addMenuItem(this._details);

        this.refresh();
        this._timer = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 300, () => {
            this.refresh();
            return GLib.SOURCE_CONTINUE;
        });
    }

    refresh() {
        const script = this._extension.dir.get_child('usage.py').get_path();
        const proc = Gio.Subprocess.new(
            ['python3', script],
            Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
        );
        proc.communicate_utf8_async(null, null, (source, result) => {
            try {
                const [, stdout] = source.communicate_utf8_finish(result);
                const data = JSON.parse(stdout);
                if (!data.ok)
                    throw new Error(data.error ?? 'Usage unavailable');
                this._label.set_text(`Codex ${data.primary_remaining}% · ${data.weekly_remaining}%`);
                this._details.label.text = `${data.plan} plan — 5-hour: ${data.primary_remaining}% remaining (${data.primary}% used), weekly: ${data.weekly_remaining}% remaining (${data.weekly}% used)`;
            } catch (error) {
                this._label.set_text('Codex —');
                this._details.label.text = `Usage unavailable: ${error.message}`;
            }
        });
    }

    destroy() {
        if (this._timer)
            GLib.source_remove(this._timer);
        super.destroy();
    }
});

export default class CodexUsageExtension extends Extension {
    enable() {
        this._indicator = new UsageIndicator(this);
        Main.panel.addToStatusArea(this.uuid, this._indicator, 1, 'right');
    }

    disable() {
        this._indicator?.destroy();
        this._indicator = null;
    }
}
