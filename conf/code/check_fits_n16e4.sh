#!/bin/bash
# Verify the N=1.6e5 GMM fit set is the EXACT 24-config grid before any b* selection.
# The 2026-09-22 05:55 BLOCKER was b* chosen from a SUBSET; counting files is not enough,
# the set must match the pre-registered n=1e4 grid config-for-config.
cd /home/HTJ/t2/conf
ref=$(ls results/gmm_fits_D2/*n10000*.npz | sed 's#.*/fit_##; s/_n10000.npz//' | sort)
got=$(ls results/gmm_fits_D2_n16e4/*n160000*.npz 2>/dev/null | sed 's#.*/fit_##; s/_n160000.npz//' | sort)
echo "reference configs : $(echo "$ref" | wc -l)"
echo "n=1.6e5 present   : $(echo "$got" | grep -c .)"
miss=$(comm -23 <(echo "$ref") <(echo "$got"))
extra=$(comm -13 <(echo "$ref") <(echo "$got"))
[ -n "$miss" ]  && { echo "MISSING:"; echo "$miss" | sed 's/^/  /'; }
[ -n "$extra" ] && { echo "UNEXPECTED EXTRA:"; echo "$extra" | sed 's/^/  /'; }
[ -z "$miss" ] && [ -z "$extra" ] && echo "SET OK -- identical to the pre-registered grid, safe to select b*"
