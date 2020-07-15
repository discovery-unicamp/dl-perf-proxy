function fail()
{
    echo "FAIL: $@"
    exit 1
}

echo "Plotting charts for results on execution-times/*/*/*.json"


for cs_dir in execution-times/*; do
    echo "Processing computing system $cs_dir"
    cs=`basename ${cs_dir}`
    python3 ./plot-epoch_accuracy_vs_execution_time.py ${cs_dir}/*/*.json -o "accuracy_vs_execution_time-cs_${cs}.pdf"
    python3 ./plot-epoch_accuracy_vs_execution_time.py --ignore_first_iteration ${cs_dir}/*/*.json -o "accuracy_vs_execution_time-skip_first_step-cs_${cs}.pdf"
done

gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all-accuracy_vs_execution_time-cs.pdf accuracy_vs_execution_time-cs_*.pdf
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all-accuracy_vs_execution_time-skip_first_step-cs.pdf accuracy_vs_execution_time-skip_first_step-cs_*.pdf

# Read log files from logs directory, extract execution times and organize them on execution-times/VMTYPE/BS/EXP.json
for bs in 256 512 1024 2048; do
    echo "Processing batch size $bs"
    python3 ./plot-epoch_accuracy_vs_execution_time.py execution-times/*/${bs}/*.json -o "accuracy_vs_execution_time-bs_${bs}.pdf"
    python3 ./plot-epoch_accuracy_vs_execution_time.py --ignore_first_iteration execution-times/*/${bs}/*.json -o "accuracy_vs_execution_time-skip_first_step-bs_${bs}.pdf"
done

gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all-accuracy_vs_execution_time-bs.pdf accuracy_vs_execution_time-bs_*.pdf
gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=all-accuracy_vs_execution_time-skip_first_step-bs.pdf accuracy_vs_execution_time-skip_first_step-bs_*.pdf

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
