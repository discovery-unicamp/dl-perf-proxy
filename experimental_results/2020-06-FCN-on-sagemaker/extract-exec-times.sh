function fail()
{
    echo "FAIL: $@"
    exit 1
}

# Read log files from logs directory, extract execution times and organize them on execution-times/VMTYPE/BS/EXP.json
for logf in logs/result-*-*-e*.txt; do
    echo "Extracting times from ${logf}"
    VMTYPE=`echo "${logf}" | cut -d- -f2-3`
    if [ "${VMTYPE}x" == "x" ]; then
	echo "Could not identify VMTYPE on log filename: ${logf}"
    else
	BS=`echo "${logf}" | cut -d- -f4`
	if [ "${BS}x" == "x" ]; then
	    echo "Could not identify BS on log filename: ${logf}"
	else
	    EXP=`echo "${logf}" | cut -d- -f5 | cut -d\. -f1`
	    if [ "${BS}x" == "x" ]; then
		echo "Could not identify EXP on log filename: ${logf}"
	    else
		echo "[${VMTYPE},${BS},${EXP}]"
		OUTDIR="execution-times/${VMTYPE}/${BS}/"
		mkdir -p "${OUTDIR}"
		python3 ./parse-exec-times.py < "${logf}" > "${OUTDIR}/${EXP}.json" || fail "Error when parsing log ${logf}"
	    fi
	fi
    fi
done
    
