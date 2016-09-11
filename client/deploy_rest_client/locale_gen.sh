#!/bin/bash

xgettext --language=Python --keyword=_ --output=i18n/client.pot --from-code=UTF-8 {client.py,constant.py}

