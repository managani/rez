from rezgui.qt import QtCore, QtGui
from rezgui.widgets.ToolWidget import ToolWidget
from rezgui.util import get_icon, create_pane
from rezgui.objects.App import app


class _TreeNode(QtGui.QLabel):

    clicked = QtCore.Signal()

    def __init__(self, item, txt, parent=None):
        super(_TreeNode, self).__init__(txt, parent)
        self.item = item
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        super(_TreeNode, self).mouseReleaseEvent(event)
        self.clicked.emit()
        if event.button() == QtCore.Qt.LeftButton:
            self.item.setExpanded(not self.item.isExpanded())


class ContextToolsWidget(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(ContextToolsWidget, self).__init__(parent)
        self.context = None
        self.tool_widgets = {}

        icon = get_icon("package")
        self.package_icon = QtGui.QIcon(icon)

        h = self.header()
        h.stretchLastSection()
        h.setResizeMode(QtGui.QHeaderView.Fixed)
        h.setVisible(False)

        self.setColumnCount(2)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        app.process_tracker.instanceCountChanged.connect(self._instanceCountChanged)

    def clear(self):
        super(ContextToolsWidget, self).clear()
        self.context = None
        self.tool_widgets = {}

    def set_context(self, context):
        self.clear()

        variants = (x for x in context.resolved_packages if x.tools)
        for variant in sorted(variants, key=lambda x: x.name):
            if not variant.tools:
                continue

            item = QtGui.QTreeWidgetItem(self)
            item.setIcon(0, self.package_icon)
            widget = _TreeNode(item, variant.qualified_package_name)
            widget.clicked.connect(self._clear_selection)
            self.setItemWidget(item, 1, widget)

            for tool in sorted(variant.tools):
                item_ = QtGui.QTreeWidgetItem(item)
                widget = ToolWidget(context, tool, app.process_tracker)
                widget.clicked.connect(self._clear_selection)
                self.setItemWidget(item_, 1, widget)
                self.tool_widgets[tool] = widget

        self.resizeColumnToContents(0)
        self.context = context

    def _clear_selection(self):
        self.setCurrentIndex(QtCore.QModelIndex())
        self.clearSelection()

    def _instanceCountChanged(self, context_id, tool_name, num_procs):
        if self.context is None or context_id != id(self.context):
            return

        widget = self.tool_widgets.get(str(tool_name))
        if widget:
            widget.set_instance_count(num_procs)