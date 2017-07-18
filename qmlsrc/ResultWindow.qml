import QtQuick 2.8
import QtQuick.Window 2.2
import QtQuick.Controls 2.1
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1

Window {
    id: root
    property var model: []
    property var args: []
    signal plotResult(var args)

    width: 600
    height: 400
    Component {
        id: tableViewColumnComponent
        TableViewColumn {

            width: 200
        }
    }

    Page {
        anchors.fill: parent
        header: ToolBar {
            height: 28
            ToolButton {
                text: "Plot"
                onClicked: {
                    setupPlotDialog.open()
                }
            }
        }

        Page {
            anchors.fill: parent
            header: TabBar {
                id: tabbar
                Repeater {
                    model: root.model
                    delegate: TabButton {
                        text: index
                        width: 100
                    }
                }
            }

            SwipeView {
                id: swipeView
                currentIndex: tabbar.currentIndex
                anchors.fill: parent
                Repeater {
                    model: root.model
                    delegate: TableView {
                        id: tableView
                        property int tableIndex: index
                        Component.onCompleted: {
                            for (var i in root.args) {
                                var a = args[i].toString()
                                tableView.addColumn(tableViewColumnComponent.createObject(tableView,{"title": a, "role": a}))
                            }

                        }
                        itemDelegate: Text {
                            elide: Text.ElideRight
                            anchors.fill: parent
                            Component.onCompleted: {
                                var d = root.model[tableIndex][args[styleData.column]][styleData.row]
                                text = d
                            }
                        }
                        model: modelData['t']
                    }

                }
            }
        }
    }


    SetupPlotDialog {
        id: setupPlotDialog
        model: args


        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: {
            var argslist = [xarg.toString(), yarg.toString()]
            if (zchecked) {
                argslist.push(zarg.toString())
            }
            plotResult(argslist)
        }
    }



}
