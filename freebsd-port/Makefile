# Created by: Jeremy Johnston <jeremy@smart-serv.net>
# $FreeBSD$

PORTNAME=	tuptime
PORTVERSION=	3.2.01
CATEGORIES=	sysutils

MAINTAINER=	jeremy@smart-serv.net
COMMENT=	Reporting the historical and statistical running time of the system

LICENSE=	GPLv2

RUN_DEPENDS=    ${PYTHON_PKGNAMEPREFIX}sqlite3>=2.7:${PORTSDIR}/databases/py-sqlite3

USES=		python:run shebangfix

NO_BUILD=	yes
USE_RC_SUBR=	tuptime

USE_GITHUB=	yes
GH_ACCOUNT=	rfrail3
GH_PROJECT=	tuptime
GH_TAGNAME=	78ad2be

SUB_FILES=	pkg-message
python_OLD_CMD=         /usr/bin/env python
SHEBANG_FILES=          ${WRKSRC}/latest/tuptime ${WRKSRC}/scripts/*

PLIST_FILES=	bin/tuptime \
		${EXAMPLESDIR}/db-tuptime-migrate.sh \
		${EXAMPLESDIR}/db-tuptime-migrate-3.0-to-3.1.sh

do-install:
	@${MKDIR} ${STAGEDIR}${EXAMPLESDIR}
	${INSTALL_SCRIPT} ${WRKSRC}/latest/tuptime ${STAGEDIR}${PREFIX}/bin/tuptime
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/db-tuptime-migrate.sh ${STAGEDIR}${EXAMPLESDIR}/db-tuptime-migrate.sh
	${INSTALL_SCRIPT} ${WRKSRC}/scripts/db-tuptime-migrate-3.0-to-3.1.sh ${STAGEDIR}${EXAMPLESDIR}/db-tuptime-migrate-3.0-to-3.1.sh

.include <bsd.port.mk>
