# KIN and KINgaroo

[![](https://anaconda.org/bioconda/kin/badges/downloads.svg)](https://anaconda.org/bioconda/kin)

KIN is a Hidden-Markov-Model-based approach to identify identity-by-descent fragments and to estimate the degree of relatedness from ancient DNA data. KIN can accurately determine up to 3rd-degree relatives and differentiate between sibling and parent-child relationships with as little as 0.05x coverage.

KINgaroo is a software to generate input files for KIN from bamfiles. Optionally, KINgaroo incorporates an adjustment for contamination and an additional model to estimate the location of long runs of homozygosity. This helps KIN to improve classification accuracy.

## Conda Environment

KIN and KINgaroo require Python 3.8+ and rely on a number of non-standard libraries. Here is the list of these dependencies with the versions that we used:

- scipy (version 1.8.0)
- numpy (version 1.21.1)
- pandas (version 1.3.1)
- numba (version 0.55.1)
- pysam (version 0.19.0)
- pybedtools (version 0.9.0)
- samtools (version 1.15)
- bcftools (version 1.15)

We recommend using a conda environment with all these dependencies. You can use the `kin-3.1.3-environment.yml` file in the `pypackage` folder to create such an environment:


```
conda env create -f kin-3.1.3-environment.yml
```
## Installation

After downloading or cloning this repository, you will find the folders `kin` and `kingaroo` in the `pypackage` folder. You can install KINgaroo from the terminal:

```
pip3 install _path_to_kingaroo
```
Similarly, install KIN:

```
pip3 install _path_to_kin
```

## Running KINgaroo

**IMPORTANT: Please make sure that your input bamfiles are filtered (remove duplicates, and apply standard filters for quality control). Unfiltered duplicates may affect the results.**

You can run KINgaroo from the terminal by typing:
```
  KINgaroo [-h] -bam  -bed  -T  -cnt  [-c] [-i] [-t] [-cest] [-d] [-tar] [-cont] [-r] [-p]
```

Here optional inputs are shown in [].

- h: Help
- test: Check if input files are in the correct format
- bam: Path to directory containing bamfiles with chromosomes (represented by 1,2,..,X,Y)
- bed: Path to tab-separated .bed file containing chromosome (1,2,..,X,..), reference, and alternate alleles at all available positions. In the bed file, provide position and position+1 in the 2nd and 3rd columns ([see example file](example_files/bedfile.bed)).
- T: Path to file ([see example file](example_files/targets.txt)) containing a list of all bamfiles (without extension .bam) to be used in the analysis
- cnt: We provide three options for contamination correction:
    - 0: No contamination correction
    - 1: Contamination correction using divergence between the target population and contaminating population. Please enter the path to an indexed compressed vcf file [-d] with an individual each from target [-tar] and contaminating populations [-cont]. Also required for this step: path to contamination estimates file [-cest]
    - 0 < cnt < 1: Contamination correction using divergence value entered here (0 < cnt < 1). Also required for this step: path to contamination estimates file [-cest]
- c: Number of cores (by default: all available cores)
- i: Size of genomic windows in int, Options:10000000, 1000000 (by default we use 10000000)
- t: Minimum number of nonzero windows for a library to be included in the estimation for p_0 (by default:10)
- cest: File with contamination estimates with 2 tab-separated columns: name, contamination
- d: Compressed and indexed vcf file for the calculation of divergence between the target and contaminating populations. Please make sure that your vcf file has genotypes [GT] represented in one of the following formats: X|Y (for phased files), X/Y (for unphased files), X (for pseudohaploids). Here X,Y are 0/1 for ancestral/derived allele
- tar: Name of individual from the target population in [-d]
- cont: Name of individual from the contaminating population in [-d]
- r: Enter 1 to estimate long ROH, 0 to skip (by default 1)
- p: p_0 estimate given by the user (by default: Estimated from the data)
- N: Total number of chromosome pairs. Default=22
- n: You can optionally specify the noisy windows that should be filtered out in a file with a list of window indexes (0-based)
- s: Enter 0 if your bamfiles are already indexed and sorted to skip these operations. By default, the bamfiles will be indexed and sorted

## Running KIN

```
KIN [-h] -I  -O  -T  [-r] [-c] [-t] [-p] [-i]
```

- h: Help
- I: Path to the folder where you ran KINgaroo
- O: Output location for KIN
- r: Location of the directory containing ROH estimates (by default: same as -I)
- c: Cores (by default: all available cores)
- t: Minimum number of sites in a window from which ROH estimates are reliable used (by default: 10)
- p: p_0 estimate given by the user (by default: Estimated from the data)

## Output

The final results are available in the file `KIN_results.csv` ([see example file](example_files/KIN_results.csv))

The output file has the following columns:
- Pair: Name of all pairs
- Relatedness: Most likely relation
- Second Guess: Second most likely relation (outside the degree of the most likely relation)
- Log Likelihood Ratio: Log likelihood ratio for the above-mentioned relations
- Within Degree Second Guess: Second most likely relation within the relatedness degree of the most likely relation
- Within Degree Log Likelihood Ratio: Log likelihood ratio for within-degree relations
- k0: Proportion of genome with no IBD sharing
- k1: Proportion of genome with one chromosome in IBD
- k2: Proportion of genome with both chromosomes in IBD
- IBD Length: Total number of windows in IBD
- IBD Number: Total number of IBD segments

We distinguish between the columns 'Second Guess' and 'Within Degree Second Guess' as well as between 'Log Likelihood Ratio' and 'Within Degree Log Likelihood Ratio'. This becomes important in the case of classification to siblings or parent-child, where we want to know how certain we are that the pair is first degree relative as indicated by 'Log Likelihood Ratio', but
we also want to know the certainty associated with classification as parent-child compared to siblings or vice-versa.

## Interpreting results

We recommend users to filter out the results with lower than 1.0 Log Likelihood Ratio, as these results may not be reliable. Similarly, to differentiate between siblings/parent-child, use results with Within Degree Log Likelihood Ratio >1. We provide following additional files (in the folder for KINgaroo) that may be informative to users:

- hmm_parameters/p_0.txt : It has one float value representing average pairwise difference for unrelated individuals. While comparing to other methods like READ, one can compare p_0 to corresponding measure for background diversity.<br>
- hbd_results/pw_[sample_name].csv : For each genomic window, it shows in columns the chromosome, number of overlapping sites, and probability of seeing no ROH in the window.

In the folder with KIN results, likfiles/[sample_pair].csv shows an array of log likelihoods corresponding to the different cases of relatedness (order: 'Unrelated','5th Degree','4th Degree','3rd Degree','Grandparent-Grandchild','Half-siblings','Avuncular','Siblings', 'Parent-Child','Identical']). It may be useful to look at this array for a pair of individuals to see the log likelihood ratio for any two relatedness cases. For very low-coverage data, all log likelihood values will look similar.

## Subsetting individuals for estimation of p_0

In many cases the user may have samples that are very low coverage or highly contaminated, and the user would like to exclude these samples while estimating p_0 (background diversity in the population). To do this run kingaroo with target file (-T) containing only the samples that you want to use in estimation of p_0. From this run you will get output file hmm_parameters/p_0.txt containing p_0 and filtered_windows.txt containing list of windows with lot of noise. Now you can run kingaroo in another folder with the target file (-T) containing all the samples that you want to include for relatedness analysis using options -p_0 [the value in "hmm_parameters/p_0.txt"] -n [location of "filtered_windows.txt"]. Then run kin with the option -p [the value in hmm_parameters/p_0.txt].

## Limitations

This software assumes one single population. If there is structure in your dataset, apply KIN and KINgaroo to sub-populations independently. The current implementation requires atleast 3 samples, and not more than around 150 samples.
