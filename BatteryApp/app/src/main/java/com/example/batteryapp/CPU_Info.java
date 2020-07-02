package com.example.batteryapp;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
import java.util.regex.Pattern;

public class CPU_Info {
    // private static DecimalFormat df = new DecimalFormat("0.00");

    /** Function to read the current usage percent of the cpu. For each core:
     *      * read the current scaling frequency,
     *      * read the mininum frequency,
     *      * read the maximum frequency.
     * The total usage percentage is the sum( individual_core_usage ) / number_of_cores.
     * @return The total usage percentage.
     */
    public float readCpuPercentNow(){
        // MainActivity currActivity = new MainActivity();
        // String output = "";

        File[] cpuFiles = getCPUs(); // Get number of CPUs
        float totalPercent = 0;
        String scaling_cur_freq;
        String cpuinfo_min_freq;
        String cpuinfo_max_freq;

        for (File cpuFile : cpuFiles) {
            // Files to be read
            String path_scaling_cur_freq =
                    cpuFile.getAbsolutePath() + "/cpufreq/scaling_cur_freq";
            String path_cpuinfo_min_freq =
                    cpuFile.getAbsolutePath() + "/cpufreq/cpuinfo_min_freq";
            String path_cpuinfo_max_freq =
                    cpuFile.getAbsolutePath() + "/cpufreq/cpuinfo_max_freq";

            // Commands to be executed //
            scaling_cur_freq = cmdCat(path_scaling_cur_freq);
            cpuinfo_min_freq = cmdCat(path_cpuinfo_min_freq);
            cpuinfo_max_freq = cmdCat(path_cpuinfo_max_freq);

            scaling_cur_freq = (scaling_cur_freq.equals("")) ? "0" : scaling_cur_freq;
            cpuinfo_min_freq = (cpuinfo_min_freq.equals("")) ? "0" : cpuinfo_min_freq;
            cpuinfo_max_freq = (cpuinfo_max_freq.equals("")) ? "0" : cpuinfo_max_freq;

            // output = output + myFormat(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            totalPercent += getUsage(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            // output = ( (i % 2) != 0) ? output + "\n" : output + " | " ;
        }
        // currActivity.setTempText(output);
        return totalPercent / cpuFiles.length;
    }

    /* Debug function to check if frequencies run as expected. */
    /*private String myFormat(String cur_freq, String cpu_min_freq, String cpu_max_freq){
        float freq = (float) Integer.valueOf(cur_freq) / (1000 * 1000);
        float min_freq = (float) Integer.valueOf(cpu_min_freq) / (1000 * 1000);
        float max_freq = (float) Integer.valueOf(cpu_max_freq) / (1000 * 1000);
        String currFormat = String.format( "%s [%s - %s]", df.format(freq), df.format(min_freq), df.format(max_freq));
        return currFormat;
    }*/

    /** Function to get the percentage of usage between min and max frequency.
     * Must be called for each core of the CPU.
     * @param cur_freq      -> String with the current scaling frequency of the core.
     * @param cpu_min_freq  -> String with the min frequency of the core.
     * @param cpu_max_freq  -> String with the max frequency of the core.
     * @return percent      -> Float contains the usage percentage.
     */
    private float getUsage(String cur_freq, String cpu_min_freq, String cpu_max_freq){
        float freq     = (float) Integer.parseInt(cur_freq) / (1000 * 1000);
        float min_freq = (float) Integer.parseInt(cpu_min_freq) / (1000 * 1000);
        float max_freq = (float) Integer.parseInt(cpu_max_freq) / (1000 * 1000);
        float percent  = (float) 0.0;
        if (max_freq > min_freq){
            percent = (freq - min_freq) / (max_freq - min_freq);
        }
        return percent * 100;
    }

    /**
     * Get file list of the pattern /sys/devices/system/cpu/cpu[0..9]
     * @return files -> File array with the files matched the above pattern.
     */
    private File[] getCPUs(){
        class CpuFilter implements FileFilter {
            @Override
            public boolean accept(File pathname) {
                return Pattern.matches("cpu[0-9]+", pathname.getName());
            }
        }

        File dir = new File("/sys/devices/system/cpu/");
        return dir.listFiles(new CpuFilter());
    }

    /** Function to read the files associated with each core.
     * For reading them the cat command will be used
     * @param f -> String with the name of each file.
     * @return the content of each file
     */
    private String cmdCat(String f){
        String[] command = {"cat", f};
        StringBuilder cmdReturn = new StringBuilder();

        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            Process process = processBuilder.start();

            InputStream inputStream = process.getInputStream();
            int cha;

            while ((cha = inputStream.read()) != -1) {
                if (cha != '\n') {
                    cmdReturn.append((char) cha);
                }
            }

            return cmdReturn.toString();
        } catch (IOException e) {
            System.out.println(e.toString());
            return "";
        }
    }

}
