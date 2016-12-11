.DUMMY: package
package:
	acbuild begin
	acbuild set-name htcondor
	acbuild copy venv .venv
	acbuild copy htcondor_collector.py htcondor_collector.py
	acbuild set-exec ./.venv/bin/python htcondor_collector.py
	acbuild write snap-plugin-collector-htcondor-linux-x86_64.aci
	acbuild end
