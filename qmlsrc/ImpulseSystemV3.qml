import QtQuick 2.8
import QtQuick.Window 2.2
import QtQuick.Controls 2.1
import QtQuick.Controls 1.4 as Controls1
import QtQuick.Layouts 1.1
import Qt.labs.platform 1.0 as Dialogs

Window {
    id: window
    visible: true
    width: 1024
    height: 600
    title: qsTr("ImpulseProblemV3.py")
    property int dim: 1
    property var args: []
    property var diffSysList: []
    property var impOperatorList: []
    property var points: []
    property var theta: []



    signal calculate(double maxtime, double h)
    signal openFile(string url)
    signal saveFile(string url)
    function calculateStarted() {
        loadIndicator.running = true
    }
    function calculateFinished() {
        loadIndicator.running = false
    }
    function error(title, msg) {
        errorDialog.title = title
        errorDialog.message = msg
        loadIndicator.running = false
        errorDialog.open()
    }
    onDimChanged: {
        clearViews()
    }
    Component.onCompleted: clearViews()

    function clearViews() {
        var diffSys = []
        var impop = []
        args = ["t"]
        for (var i = 0; i < dim; ++i) {
            var a = "x%1".arg(i+1)
            args.push(a)
            var d = {}
            d.index = i
            d.left = "d" + a + "/dt"
            d.right = "0"
            diffSys.push(d)
            var imp = {}
            imp.index = i
            imp.left = a
            imp.right = "0"
            impop.push(imp)
        }

        diffSysList = diffSys
        impOperatorList = impop
        points = []
        pointsView.keys = args
        theta = []
    }

    Page {

        anchors.fill: parent
        header: ToolBar {
            Row {
                ToolButton {
                    id: dimlabel
                    text: "Dim: " + dim
                    onClicked: dimDialog.open()
                }
                ToolButton {
                    text: "Посчитать"
                    onClicked: calculateDialog.open()
                }
                ToolButton {
                    text: "Открыть"
                    onClicked: {
                        fileDialog.fileMode = Dialogs.FileDialog.OpenFile
                        fileDialog.open()
                    }
                }
                ToolButton {
                    text: "Сохранить"
                    onClicked:{
                        fileDialog.fileMode = Dialogs.FileDialog.SaveFile
                        fileDialog.open()
                    }
                }
            }
        }

        Controls1.SplitView {
            id: rootSplit
            anchors.fill: parent
            orientation: Qt.Horizontal
            Controls1.SplitView {
                Layout.minimumWidth: 200
                orientation: Qt.Vertical
                width: 400
                SystemView {
                    id: diffSysView
                    headerTitle: "Дифференциальная система"
                    Layout.minimumHeight: 100
                    height: 250
                    model: window.diffSysList
                }
                SystemView {
                    id: impOperatorView
                    headerTitle: "Импульсный оператор"
                    Layout.minimumHeight: 100
                    model: window.impOperatorList
                }
            }

            Controls1.SplitView {
                Layout.minimumWidth: 200
                orientation: Qt.Vertical
                PointsView {
                    id: pointsView
                    headerTitle: "Начальные точки"
                    Layout.minimumHeight: 100
                    height: 250
                    model: window.points
                    onAddPoint: {
                        var p = {}
                        for (var i in keys) {
                            p[keys[i]] = "0"
                        }
                        window.points.push(p)
                        window.points = window.points
                    }
                }
                ThetaView {
                    id: thetaView
                    headerTitle: "Промежутки между импульсами θ=[θ1, θ2, ...]"
                    Layout.minimumHeight: 100
                    model: window.theta
                }
            }
        }



    }

    Dialog {
        id: calculateDialog
        padding: 20
        margins: 40
        modal: true
        Column {
            id: column

            Row {
                anchors.right: parent.right
                anchors.rightMargin: 0
                Label {
                    text: "Конечное время: "
                    anchors.verticalCenter: parent.verticalCenter
                }
                TextField {
                    id: timeField
                    anchors.verticalCenter: parent.verticalCenter
                    selectByMouse: true
                    height: 36
                    text: "1"
                }
            }

            Row {
                anchors.right: parent.right
                anchors.rightMargin: 0
                Label {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Шаг по сетке t: "
                }
                TextField {
                    id: stepField
                    anchors.verticalCenter: parent.verticalCenter
                    selectByMouse: true
                    height: 36
                    text: "0.01"
                }
            }
        }
        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            var t = parseFloat(timeField.text)
            var h = parseFloat(stepField.text)
            if (h > 0 && !isNaN(t)) {
                calculate(t, h)
            }
        }
    }
    Dialog {
        id: dimDialog
        padding: 20
        margins: 40
        modal: true
        Column {

            Row {
                anchors.right: parent.right
                anchors.rightMargin: 0
                Label {
                    text: "Новая размерность: "
                    anchors.verticalCenter: parent.verticalCenter
                }
                TextField {
                    id: dimField
                    anchors.verticalCenter: parent.verticalCenter
                    selectByMouse: true
                    height: 36
                    text: dim
                }
            }
        }
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: {
            var newdim = parseInt(dimField.text)
            if (newdim > 0 && newdim != window.dim) {
                window.dim = newdim
            }
        }
        onOpened: {
            dimField.text = window.dim
        }
    }



    Dialog {
        id: errorDialog
        padding: 20
        margins: 40
        property alias message: messageText.text
        Text {
            id: messageText
        }
    }

    Dialogs.FileDialog {
        id: fileDialog
        onAccepted: {
            if (fileMode == Dialogs.FileDialog.OpenFile) {
                openFile(file)
            } else if (fileMode == Dialogs.FileDialog.SaveFile) {
                saveFile(file)
            }
        }
        defaultSuffix: "isv3"
        nameFilters: ["ImpSystem File (*.isv3)", "All files (*)"]
    }

    BusyIndicator {
        id: loadIndicator
        width: 80
        height: 80

        running: false
        anchors.centerIn: parent
    }

}
