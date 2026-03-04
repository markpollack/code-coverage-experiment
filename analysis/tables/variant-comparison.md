# Variant Comparison

## Summary

| Variant | Pass% | Avg Cov% | Avg T3 | Avg Golden | Avg Eff | Total Cost | Phases |
|---------|-------|----------|--------|------------|---------|------------|--------|
| control | 80.0% | 85.7 | 0.613 | 0.62 | 0.827 | $4.22 | 1ph |
| variant-a | 100.0% | 84.2 | 0.713 | 0.656 | 0.938 | $4.06 | 1ph |
| variant-b | 100.0% | 95.6 | 0.763 | 0.745 | 0.932 | $4.67 | 1ph |
| variant-c | 100.0% | 84.9 | 0.75 | 0.684 | 0.854 | $5.13 | 1ph |
| variant-d | 100.0% | 94.1 | 0.703 | 0.659 | 0.746 | $8.39 | 2ph |

## Per-Item T3 Practice Adherence

| Item | control | variant-a | variant-b | variant-c | variant-d |
|------|------|------|------|------|------|
| gs-accessing-data-jpa | 0.5 | 0.6 | **0.733** | 0.683 | **0.733** |
| gs-messaging-stomp-websocket | 0.45 | **0.65** | 0.55 | 0.5 | 0.5 |
| gs-reactive-rest-service | 0.733 | 0.817 | 0.817 | **0.9** | 0.733 |
| gs-rest-service | 0.667 | 0.817 | **0.883** | **0.883** | **0.883** |
| gs-securing-web | 0.717 | 0.683 | **0.833** | 0.783 | 0.667 |

## Per-Item Golden Test Similarity

| Item | control | variant-a | variant-b | variant-c | variant-d |
|------|------|------|------|------|------|
| gs-accessing-data-jpa | 0.635 | 0.622 | **0.875** | **0.875** | 0.743 |
| gs-messaging-stomp-websocket | 0.639 | **0.773** | 0.68 | 0.45 | 0.507 |
| gs-reactive-rest-service | 0.601 | **0.83** | 0.668 | 0.451 | 0.73 |
| gs-rest-service | 0.483 | 0.36 | 0.5 | **0.643** | 0.4 |
| gs-securing-web | 0.742 | 0.696 | **1.0** | **1.0** | 0.917 |

## Per-Item Coverage (%)

| Item | control | variant-a | variant-b | variant-c | variant-d |
|------|------|------|------|------|------|
| gs-accessing-data-jpa | 94.595 | 94.595 | 94.595 | 94.595 | 94.595 |
| gs-messaging-stomp-websocket | 92.308 | 84.615 | 92.308 | 88.462 | 84.615 |
| gs-reactive-rest-service | 78.947 | 78.947 | 100.0 | 78.947 | 100.0 |
| gs-rest-service | 71.429 | 71.429 | 100.0 | 71.429 | 100.0 |
| gs-securing-web | 91.304 | 91.304 | 91.304 | 91.304 | 91.304 |

## Per-Item Efficiency

| Item | control | variant-a | variant-b | variant-c | variant-d |
|------|------|------|------|------|------|
| gs-accessing-data-jpa | 0.96 | 0.94 | 0.943 | 0.66 | 0.503 |
| gs-messaging-stomp-websocket | 0.796 | 0.883 | 0.973 | 0.964 | 0.925 |
| gs-reactive-rest-service | 0.908 | 0.953 | 0.959 | 0.855 | 0.725 |
| gs-rest-service | 0.789 | 0.955 | 0.851 | 0.835 | 0.842 |
| gs-securing-web | 0.68 | 0.962 | 0.933 | 0.955 | 0.733 |
