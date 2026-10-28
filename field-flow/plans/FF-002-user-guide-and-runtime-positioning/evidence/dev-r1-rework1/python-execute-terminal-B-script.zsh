read -r FF_PROJECT
read -r FF_LESSON
cd "$FF_PROJECT"
sleep 0 &
FF_PID=$!
wait "$FF_PID"
FF_EXIT=$?
printf "B runtime PID=%s exit=%s\n" "$FF_PID" "$FF_EXIT"
printf "B ready\n"
read -r FF_CHECK_READY
cat "$FF_LESSON/execute-lesson/fixture/report.json"
cat "$FF_LESSON/execute-lesson/stderr.txt"
lsof -nP -iTCP:32102 -iTCP:32103 -iTCP:32880 -sTCP:LISTEN
printf "checking runtime PID=%s\n" "$FF_PID"
ps -p "$FF_PID" -o pid=,stat=,command=

FF_PS_EXIT=$?
printf "B ps exit=%s\n" "$FF_PS_EXIT"
[[ "$FF_PID" == <1-> && "$FF_PS_EXIT" == 1 ]] || exit 10
[[ ! -v FF_FIXTURE_EXIT ]] || exit 11
printf "B fixture variable remains unset\n"
