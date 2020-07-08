function fail()
{
    echo "FAIL: $@"
    exit 1
}

# Read log files from logs directory, extract execution times and organize them on execution-times/VMTYPE/BS/EXP.json
echo "Plotting charts for results on execution-times/*/*/*.json"

for jfile in execution-times/*/*/*.json; do
    OUTDIR=`dirname "${jfile}"`
    EXP=`basename "${jfile}" .json`
    VMTYPE=`echo "${OUTDIR}" | cut -d/ -f2`
    BS=`echo "${OUTDIR}" | cut -d/ -f3`
    OUTFILE="${OUTDIR}/${EXP}-step_times_per_epoch.pdf"
    echo "Processing $jfile => ${OUTFILE}"
    python3 ./plot-step_times_per_epoch.py -t "${VMTYPE} / ${BS} / ${EXP}" -o "${OUTFILE}" < "${jfile}" || \
	fail "Error when generating ${OUTFILE}"
done
    
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all-step_times_per_epoch.pdf execution-times/*/*/*-step_times_per_epoch.pdf
