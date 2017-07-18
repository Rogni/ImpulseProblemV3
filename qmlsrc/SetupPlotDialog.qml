import QtQuick 2.8
import QtQuick.Controls 2.1
import QtQuick.Dialogs 1.2 as Dialogs

Dialogs.Dialog {
    id: root
    width: 300
    height: 300
    property var model

    property alias xarg: comboBox.currentText
    property alias yarg: comboBox1.currentText
    property alias zarg: comboBox2.currentText
    property alias zchecked: checkDelegate.checked

    Column {
        id: column
        anchors.fill: parent
    }

    Item {
        id: item2
        height: 44
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.leftMargin: 8
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: 8

        Text {
            id: text1
            y: 14
            text: qsTr("X")
            anchors.left: parent.left
            anchors.leftMargin: 8
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 14
        }

        ComboBox {
            id: comboBox
            width: 173
            height: 40
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.verticalCenterOffset: 0
            anchors.verticalCenter: parent.verticalCenter
            model: root.model
        }
    }

    Item {
        id: item3
        height: 44
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.leftMargin: 8
        anchors.top: item2.bottom
        anchors.left: parent.left
        anchors.topMargin: 6

        Text {
            id: text2
            y: 14
            text: qsTr("Y")
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: 14
        }

        ComboBox {
            id: comboBox1
            width: 173
            height: 40
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.verticalCenter: parent.verticalCenter
            model: root.model
        }
    }

    Item {
        id: item4
        height: 44
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.leftMargin: 8
        anchors.top: item3.bottom
        anchors.left: parent.left
        anchors.topMargin: 6

        Text {
            id: text3
            y: 14
            text: qsTr("Z")
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: 14
        }

        CheckDelegate {
            id: checkDelegate
            width: 51
            anchors.left: text3.right
            anchors.leftMargin: 6
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0
        }

        ComboBox {
            id: comboBox2
            height: 40
            enabled: checkDelegate.checked
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 0
            model: root.model
        }
    }

}
