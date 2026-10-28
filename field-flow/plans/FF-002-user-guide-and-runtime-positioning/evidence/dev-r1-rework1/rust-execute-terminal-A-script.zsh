[[ ! -v FF_PID ]] || exit 12
sleep 0
FF_FIXTURE_EXIT=$?
printf "fixture exit=%s\n" "$FF_FIXTURE_EXIT"

[[ "$FF_FIXTURE_EXIT" == 0 && ! -v FF_PID ]] || exit 13
printf "A runtime variable remains unset\n"
