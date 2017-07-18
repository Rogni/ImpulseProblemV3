import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQml.Models 2.3

Page {
    id: root
    property alias headerTitle: headerLabel.text
    property var model: []
    onModelChanged: {
        visualModel.model = model
    }

    header: HeaderLabel {
        id: headerLabel
    }

    ListView {
        id: listView
        clip: true
        anchors.fill: parent
        displaced: Transition {
            NumberAnimation { properties: "y"; easing.type: Easing.OutQuad }
        }
        model: DelegateModel {
            id: visualModel
            model: root.model
            delegate: MouseArea {
                id: delegateRoot
                property int visualIndex: DelegateModel.itemsIndex
                width: root.width
                height: 40
                drag.target: icon
                Rectangle {
                    id: icon
                    width: root.width; height: 40
                    anchors {
                        horizontalCenter: parent.horizontalCenter;
                        verticalCenter: parent.verticalCenter
                    }
                    color: visualIndex%2 ? "#EEEEEE" : "#FFF"
                    radius: 3

                    Row {
                        x: 8
                        spacing: 8
                        anchors.verticalCenter: parent.verticalCenter
                        Button {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 24
                            height: 24
                            text: "-"
                            onClicked: {
                                root.model.splice(visualIndex, 1)
                                root.model = root.model
                            }
                        }
                        Label {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "θ" + (visualIndex + 1).toString() + " = "
                        }
                        TextField {
                            selectByMouse: true
                            text: modelData
                            width: 128
                            height: 32
                            anchors.verticalCenter: parent.verticalCenter
                            onTextChanged: {
                                root.model[visualIndex] = text
                            }
                        }
                    }

                    Drag.active: delegateRoot.drag.active
                    Drag.source: delegateRoot
                    Drag.hotSpot.x: 36
                    Drag.hotSpot.y: 36

                    states: [
                        State {
                            when: icon.Drag.active
                            ParentChange {
                                target: icon
                                parent: root
                            }

                            AnchorChanges {
                                target: icon;
                                anchors.horizontalCenter: undefined;
                                anchors.verticalCenter: undefined
                            }
                        }
                    ]
                }

                DropArea {
                    anchors { fill: parent; margins: 15 }

                    onEntered: visualModel.items.move(drag.source.visualIndex, delegateRoot.visualIndex)
                }
            }
         }
    }

    footer: Button {
        text: "Добавить"
        onClicked: {
            root.model.push("1")
            visualModel.model = root.model
        }
    }
}
