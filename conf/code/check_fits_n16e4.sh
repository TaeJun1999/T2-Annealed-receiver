#!/bin/bash
# Verify the N=1.6e5 GMM fit set before any b* selection.
#
# WHY THIS EXISTS: arms.load_fits() loads whatever files happen to exist ("if os.path.exists")
# and gmm_selection() then picks b* from that set -- SILENTLY.  A missing fit does not raise;
# it just shrinks the candidate grid.  That is the 2026-09-22 05:55 BLOCKER.  Counting files is
# not enough: the set must match the pre-registered grid config-for-config.
#
# Cells C1/C2/C5 (the equal-budget run) are all Nr=8, so Nr=8 completeness is what UNBLOCKS the run;
# Nr=4 (cells C3/C4, sanity only) is reported separately for record completeness.
cd /home/HTJ/t2/conf
ref=$(ls results/gmm_fits_D2/*n10000*.npz | sed 's#.*/fit_##; s/_n10000.npz//' | sort)
got=$(ls results/gmm_fits_D2_n16e4/*n160000*.npz 2>/dev/null | sed 's#.*/fit_##; s/_n160000.npz//' | sort)
miss=$(comm -23 <(echo "$ref") <(echo "$got"))
extra=$(comm -13 <(echo "$ref") <(echo "$got"))
m8=$(echo "$miss" | grep Nr8); m4=$(echo "$miss" | grep Nr4)
printf "reference %s | present %s | missing Nr8 %s | missing Nr4 %s\n" \
  "$(echo "$ref"|wc -l)" "$(echo "$got"|grep -c .)" "$(echo "$m8"|grep -c .)" "$(echo "$m4"|grep -c .)"
[ -n "$m8" ] && { echo "MISSING Nr=8 (BLOCKS the C1/C2/C5 equal-budget run):"; echo "$m8" | sed 's/^/  /'; }
[ -n "$m4" ] && { echo "missing Nr=4 (C3/C4 sanity cells only; does not block):"; echo "$m4" | sed 's/^/  /'; }
[ -n "$extra" ] && { echo "UNEXPECTED EXTRA:"; echo "$extra" | sed 's/^/  /'; }
if [ -n "$m8" ] || [ -n "$extra" ]; then echo "NOT READY"; exit 1; fi
echo "Nr=8 SET OK -- b* for C1/C2/C5 will be selected from the full pre-registered grid"; exit 0
