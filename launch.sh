#!/bin/bash

BASE_ACM="/dev/ttyACM*";
BASE_USB="/dev/ttyUSB*";

ACM_DEVICES=$(ls $BASE_ACM);
FOUND_ACM=$?;
USB_DEVICES=$(ls $BASE_USB);
FOUND_USB=$?;

echo ""
echo "ACM: $BASE_ACM";
echo "USB: $BASE_USB";
echo ""
echo "ACM Devices:" $ACM_DEVICES;
echo "Ok: $FOUND_ACM"
echo ""
echo "USB Devices:" $USB_DEVICES;
echo "Ok: $FOUND_USB"
echo ""

declare -a ARDUINOS;

if [[ "$FOUND_ACM" == "0" ]]; then
    ARDUINOS=(${ARDUINOS[@]} $ACM_DEVICES);
fi

if [[ "$FOUND_USB" == "0" ]]; then
    ARDUINOS=(${ARDUINOS[@]} $USB_DEVICES);
fi

echo "Arduinos: " ${ARDUINOS[@]};
