import tkinter as tk
from tkinter import ttk

import pytest

from tests.conftest import pump_events
from tklife.core import SkelWidget
from tklife.widgets import ModalDialog, ScrolledFrame


@pytest.fixture(scope="function")
def dialog_class():
    class Dialog(ModalDialog):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            print(self)

        @property
        def template(self):
            return [[SkelWidget(ttk.Label, label="label")]]

        def set_return_values(self):
            self.return_value = "foo"

    return Dialog


@pytest.fixture(scope="function")
def modal_dialog(master, dialog_class):
    dialog = dialog_class(master)
    return dialog


@pytest.mark.integration
class TestModalDialog:
    def test_modal_dialog_is_not_visible_by_default(self, modal_dialog: ModalDialog):
        assert not modal_dialog.winfo_ismapped()

    def test_modal_dialog_is_visible_after_show(self, modal_dialog: ModalDialog):
        actual = None

        def after():
            nonlocal actual
            actual = modal_dialog.winfo_ismapped()
            modal_dialog.destroy()

        modal_dialog.after(100, after)
        modal_dialog.show()

        assert actual == True

    def test_modal_dialog_returns_return_value_on_ok(self, modal_dialog: ModalDialog):
        modal_dialog.after(5, modal_dialog.destroy)
        actual = modal_dialog.show()

        assert actual == "foo"

    def test_modal_dialog_returns_none_on_cancel(self, modal_dialog: ModalDialog):
        modal_dialog.after(5, modal_dialog.cancel)
        actual = modal_dialog.show()

        assert actual == None

    def test_destroying_widget_in_modal_dialog_does_not_set_return_value(
        self, modal_dialog: ModalDialog
    ):
        actual = None

        def destroy_label():
            nonlocal actual
            modal_dialog.created["label"].widget.destroy()
            actual = modal_dialog.return_value

            modal_dialog.after(5, modal_dialog.destroy)

        modal_dialog.after(5, destroy_label)
        modal_dialog.show()

        assert actual is None

    def test_modal_dialog_create_creates_and_shows_dialog(
        self, master, dialog_class: ModalDialog
    ):
        actual = None

        def after():
            nonlocal actual
            modal = master.winfo_children()[-1]  # The modal is the last widget created
            actual = modal.winfo_ismapped()
            modal.destroy()

        master.after(100, after)

        dialog_class.create(master)

        assert actual == True

    def test_modal_dialog_cancels_on_escape_key(
        self, master, modal_dialog: ModalDialog
    ):
        actual = None

        def after():
            nonlocal actual
            modal_dialog.event_generate("<Escape>")

        modal_dialog.after(100, after)
        actual = modal_dialog.show()

        assert actual is None

    def test_modal_dialog_oks_on_return_key(self, master, modal_dialog: ModalDialog):
        actual = None

        def after():
            nonlocal actual
            modal_dialog.event_generate("<Return>")

        modal_dialog.after(100, after)
        actual = modal_dialog.show()

        assert actual == "foo"


@pytest.mark.integration
class TestScrolledFrame:
    @pytest.fixture
    def scrolled_frame(self, master):
        sf = ScrolledFrame(master, width=100, height=100)
        sf.pack()
        pump_events(master)
        return sf

    @pytest.fixture
    def scrolled_frame_with_labels(self, scrolled_frame):
        for i in range(20):
            ttk.Label(scrolled_frame, text=f"Label {i}").grid(row=i, column=0)
        return scrolled_frame

    def test_scrolled_frame_has_canvas(self, scrolled_frame):
        assert isinstance(scrolled_frame.canvas, tk.Canvas)

    def test_scrolled_frame_has_vertical_scrollbar(self, scrolled_frame):
        assert isinstance(scrolled_frame.v_scroll, ttk.Scrollbar)

    @pytest.mark.parametrize(
        "sequence,args", [("<Button-5>", {}), ("<MouseWheel>", {"delta": -1})]
    )
    def test_scrolled_frame_scroll_down_scrolls_canvas_down(
        self, master, scrolled_frame_with_labels, sequence, args
    ):
        pump_events(master)
        scrolled_frame_with_labels.canvas.event_generate("<Enter>")
        pump_events(master)
        scrolled_frame_with_labels.event_generate(sequence, **args)
        pump_events(master)
        assert scrolled_frame_with_labels.canvas.yview() == (
            0.06842105263157895,
            0.7657894736842106,
        )

    @pytest.mark.parametrize(
        "sequence,args", [("<Button-4>", {}), ("<MouseWheel>", {"delta": 1})]
    )
    def test_scrolled_frame_scroll_up_scrolls_canvas_up(
        self, master, scrolled_frame_with_labels, sequence, args
    ):
        # Setup
        pump_events(master)
        scrolled_frame_with_labels.canvas.yview_scroll(1, "units")
        pump_events(master)

        # Test
        scrolled_frame_with_labels.canvas.event_generate("<Enter>")
        pump_events(master)
        scrolled_frame_with_labels.event_generate(sequence, **args)
        pump_events(master)
        assert scrolled_frame_with_labels.canvas.yview() == (0.0, 0.6973684210526315)

    @pytest.mark.parametrize(
        "sequence,args",
        [
            ("<Button-5>", {}),
            ("<MouseWheel>", {"delta": -1}),
            ("<Button-4>", {}),
            ("<MouseWheel>", {"delta": 1}),
        ],
    )
    def test_scrolled_frame_does_not_scroll_canvas_if_mouse_not_over_canvas(
        self,
        master,
        scrolled_frame_with_labels,
        sequence,
        args,
    ):
        # Setup
        pump_events(master)
        scrolled_frame_with_labels.canvas.yview_scroll(1, "units")
        pump_events(master)
        scrolled_frame_with_labels.canvas.event_generate("<Enter>")
        pump_events(master)

        # Test
        scrolled_frame_with_labels.canvas.event_generate("<Leave>")
        pump_events(master)
        scrolled_frame_with_labels.event_generate(sequence, **args)
        pump_events(master)

        assert scrolled_frame_with_labels.canvas.yview() == (
            0.06842105263157895,
            0.7657894736842106,
        )
