#include <string.h>
#include <vector>
#include <stdlib.h>
#include <stdio.h>
#include <omp.h>

const char* dgemv_desc = "OpenMP dgemv.";

/*
 * This routine performs a dgemv operation
 * Y :=  A * X + Y
 * where A is n-by-n matrix stored in row-major format, and X and Y are n by 1 vectors.
 * On exit, A and X maintain their input values.
 */

void my_dgemv(int n, double* A, double* x, double* y) {

    // #pragma omp parallel
    // {
    //     int nthreads = omp_get_num_threads();
    //     int thread_id = omp_get_thread_num();
    //     printf("my_dgemv(): Hello world: thread %d of %d checking in. \n", thread_id, nthreads);
    //     printf("my_dgemv(): For actual timing runs, please comment out these printf() and omp_get_*() statements. \n");
    // }

    // insert your dgemv code here. you may need to create additional parallel regions,
    // and you will want to comment out the above parallel code block that prints out
    // nthreads and thread_id so as to not taint your timings

#pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        int local_buf_len = n / omp_get_num_threads();
        int buf_offset = thread_id * local_buf_len;
        std::vector<double> local_buf(local_buf_len);
        memcpy(local_buf.data(), &y[buf_offset], local_buf_len);

#pragma omp for
        for (int i = 0; i < local_buf_len; i++) {
            double yval = local_buf[i];
            double* Arow = &A[(buf_offset + i) * n];
            for (int j = 0; j < n; j++) {
                yval += Arow[j] * x[j];
            }
            local_buf[i] = yval;
        }

#pragma omp critical
        memcpy(&y[buf_offset], local_buf.data(), local_buf_len);
    }
}