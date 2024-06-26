#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:15:29 2022

@author: divyaratan_popli
"""

import argparse
import multiprocessing as mp
import numpy as np
from .KINgaroo_scripts import constants as C
from .KINgaroo_scripts import helpers as hel

def cli():

    parser = argparse.ArgumentParser(description="Input generation pipeline for KIN")

    parser.add_argument('-bam', '--bamfiles_location',
                        type=str, required=True,
                        help='bamfiles directory')
    parser.add_argument('-bed', '--bedfile',
                        type=str, required=True,
                        help='path to bedfile')
    parser.add_argument('-T', '--target_location',
                        type=str, required=True,
                        help='file with bamfile names that should be used without extension')
    parser.add_argument('-cnt', '--contam_parameter',
                        type=float, required=True,
                        help='Enter 0 for no contamination correction. Enter 1 for contamination correction with divergence calculated from vcf.gz. Enter divergence (between 0 and 1) if known.')
    parser.add_argument('-c', '--cores',
                        type=int,
                        help='Number of cores available')
    parser.add_argument('-i', '--interval',
                        type=int,
                        help='Length of a genomic window in bases. Options:1000000, 10000000 (by default 10000000)')
    parser.add_argument('-t', '--threshold',
                        type=int,
                        help='p_0 is estimated with all libraries that have atleast t number of informative windows (by default t=10)')
    parser.add_argument('-cest', '--contamination_estimates',
                        type=str,
                        help='tab-separated contamination estimates file with columns: name,contamination')
    parser.add_argument('-d', '--divergence_file',
                        type=str,
                        help='indexed compressed vcf file with an individual from target and contaminating populations each. Diploid Genotypes (GT) should be represented')
    parser.add_argument('-tar', '--target_ind',
                        type=str,
                        help='Name of target individual in divergence_vcf file')
    parser.add_argument('-cont', '--contaminating_ind',
                        type=str,
                        help='Name of contaminating individual in divergence_vcf file')
    parser.add_argument('-r', '--roh',
                        type=int,
                        help='Enter 1 if you need ROH estimates. Enter 0 if you already have the positions of ROH tracts (by default:1).')
    parser.add_argument('-p', '--diversity_parameter_p_0',
                        type=float,
                        help='Enter p_0 estimate for input to ROH-HMM, if quality of samples is not good enough to estimate p_0.')
    parser.add_argument('-n', '--noisy_wins',
                        type=str,
                        help='You can optionally specify the noisy windows that should be filtered out in a file with list of window indexes (0-based).')
    parser.add_argument('-test', '--test_input',
                        type=int,
                        help='Enter 1 to test your input files')
    parser.add_argument('-N', '--number_of_chromosomes',
                        type=int,
                        help='Enter the total number of chromosomes. Default=22')
    parser.add_argument('-s', '--sort_index',
                        type=int,
                        help='Enter 1 if you need to sort and index the bamfiles. Enter 0 to skip this step (by default:1).')
    return parser.parse_args()

def main():
    args = cli()

    if args.cores is None:
        cores = mp.cpu_count()
    else:
        cores = args.cores
    if args.threshold is None:
        thresh = 10
    else:
        thresh = args.threshold
    if args.interval is None:
        interval = 1e7
    else:
        interval = args.interval
    if args.roh is None:
        roh = 1
    else:
        roh = args.roh

    if args.bamfiles_location[-1] != '/':
        bamfiles_dir=args.bamfiles_location + '/'
    elif args.bamfiles_location[-1] == '/':
        bamfiles_dir=args.bamfiles_location
    if args.noisy_wins is None:
        badwins=[]
    else:
        badwins=np.loadtxt(args.noisy_wins,dtype='float', delimiter = ",")

    if args.test_input is None:
        testin = 0
    else:
        testin = args.test_input


    if args.number_of_chromosomes is None:
        n_chrm=22
    else:
        n_chrm=args.number_of_chromosomes
    CHRM=list(range(1, int(n_chrm)+1))
    if args.sort_index is None:
        sort1 = 1
    else:
        sort1 = args.sort_index

    if testin==1:
        hel.test_input(bedfile=args.bedfile, rawbams=bamfiles_dir, targetsfile=args.target_location)
    elif testin==0:
        libraries, listf, dwins, twins, id_dwins, id_twins, chrmlist = hel.pipeline1(targetsfile = args.target_location,
                                                                                     bedfile = args.bedfile,
                                                                                     cores = args.cores,
                                                                                     rawbams = bamfiles_dir,
                                                                                     interval = interval,
                                                                                     splitbams = C.splitbams,
                                                                                     bedfiles = C.bedfiles,
                                                                                     hapProbs = C.hapProbs,
                                                                                     hmm_param = C.hmm_param,
                                                                                     hbdf = C.hbdf,
                                                                                     likf = C.likf,
                                                                                     chrmf=CHRM,
                                                                                     sort1=sort1)


        if args.contam_parameter==0:
                diff_cor, total_cor, id_diff_cor, id_total_cor = dwins, twins, id_dwins, id_twins

        elif args.contam_parameter!=0:
            hel.contamFile(infile=args.contamination_estimates, outfile=C.contam_est, targets=libraries, idfile=C.id_contam_est)
            if args.contam_parameter==1:

                div= hel.divergence_vcf(args.divergence_file, args.bedfile, args.target_ind, args.contaminating_ind)
            elif args.contam_parameter>0 and args.contam_parameter<1:
                div = args.contam_parameter

            diff_cor,total_cor = hel.contamAll(diff=dwins, total=twins, cfile=C.contam_est, p_c=div)
            id_diff_cor, id_total_cor = hel.contamAll(diff=id_dwins, total=id_twins, cfile=C.id_contam_est, p_c=div)

        diff_cor, total_cor, id_diff_cor, id_total_cor, p1 = hel.data2p(diff_cor=diff_cor,
                                                                total_cor=total_cor, id_diff_cor=id_diff_cor,
                                                                id_total_cor=id_total_cor, libraries=libraries, listf=listf,
                                                                hmm_param=C.hmm_param, thresh=thresh, outdiff=C.outdiff, outtotal=C.outtotal,
                                                                id_outdiff=C.id_outdiff, id_outtotal=C.id_outtotal, badwins=badwins)
        if args.diversity_parameter_p_0 is None:
            p_0val=p1
        else:
            p_0val=args.diversity_parameter_p_0
        if roh==1:
            hel.run_hmm(diff=id_diff_cor, total=id_total_cor, chrm1=chrmlist, p1=p_0val, hbdf=C.hbdf, likf=C.likf, libraries=libraries, cores=cores)



if __name__ == '__main__':
    main()
