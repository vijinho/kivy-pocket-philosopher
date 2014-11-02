cd ~
mkdir -p .keystores
ALIAS=${ALIAS}
keytool -genkey -v -keystore ~/.keystores/${ALIAS}.keystore -alias ${ALIAS} -keyalg RSA -keysize 2048 -validity 10000
