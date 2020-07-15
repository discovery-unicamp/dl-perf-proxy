function fail()
{
    echo "FAIL: $@"
    exit 1
}

# Read log files from logs directory, extract execution times and organize them on execution-times/VMTYPE/BS/EXP.json
for logf in logs/result-*-*-e*.txt; do
    echo "Analyzing ${logf}"
    VMTYPE=`echo "${logf}" | cut -d- -f2-3`
    if [ "${VMTYPE}x" == "x" ]; then
	echo " - ERROR: Could not identify VMTYPE on log filename: ${logf}"
    else
	BS=`echo "${logf}" | cut -d- -f4`
	if [ "${BS}x" == "x" ]; then
	    echo " - ERROR: Could not identify BS on log filename: ${logf}"
	else
	    EXP=`echo "${logf}" | cut -d- -f5 | cut -d\. -f1`
	    if [ "${BS}x" == "x" ]; then
		echo " - ERROR: Could not identify EXP on log filename: ${logf}"
	    else
		echo " - [${VMTYPE},${BS},${EXP}]"
		OUTDIR="execution-times/${VMTYPE}/${BS}/"
		mkdir -p "${OUTDIR}"
		echo " - Extracting times from ${logf}"
		python3 ./parse-exec-times.py -cs "${VMTYPE}" -bs "${BS}" < "${logf}" > "${OUTDIR}/${EXP}.json" || \
		    fail "Error when parsing log ${logf}"
		echo " - Summarizing times from ${OUTDIR}/${EXP}.json"
		python3 ./training-times-summary.py < "${OUTDIR}/${EXP}.json" > "${OUTDIR}/${EXP}.summary" || \
		    fail "Error when summarizing the execution times for \"${OUTDIR}/${EXP}.json\"".
	    fi
	fi
    fi
done
    
