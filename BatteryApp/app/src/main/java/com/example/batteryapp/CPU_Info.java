package com.example.batteryapp;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
import java.util.regex.Pattern;

public class CPU_Info {

    /*
     * Find the number of cores (usually 8). Then for each core, read the
     * scaling current frequency, min and max frequncies.
     * Return the CPU Usage for the system, total usage percent for the cores / number of cores.
     */
    public float readCpuFreqNow(){
        File[] cpuFiles = getCPUs(); // Get number of CPUs

        // String output = "";
        float totalPercent = 0;
        String scaling_cur_freq = "";
        String cpuinfo_min_freq = "";
        String cpuinfo_max_freq = "";

        for(int i = 0; i < cpuFiles.length; i++) {
            // Files to be read
            String path_scaling_cur_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/scaling_cur_freq";
            String path_cpuinfo_min_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/cpuinfo_min_freq";
            String path_cpuinfo_max_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/cpuinfo_max_freq";

            // Commands to be executed //
            scaling_cur_freq = cmdCat(path_scaling_cur_freq);
            cpuinfo_min_freq = cmdCat(path_cpuinfo_min_freq);
            cpuinfo_max_freq = cmdCat(path_cpuinfo_max_freq);

            scaling_cur_freq = ( scaling_cur_freq.equals("") ) ? "0" : scaling_cur_freq;
            cpuinfo_min_freq = ( cpuinfo_min_freq.equals("") ) ? "0" : cpuinfo_min_freq;
            cpuinfo_max_freq = ( cpuinfo_max_freq.equals("") ) ? "0" : cpuinfo_max_freq;

            //output = output + myFormat(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            totalPercent += getUsage(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            //output = ( (i % 2) != 0) ? output + "\n" : output + " | " ;
        }
        //textTemp.setText(output);
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

    /*
     * From the current scaling frequency, find the percentage of usage
     * between min_freq and max_freq.
     */
    private float getUsage(String cur_freq, String cpu_min_freq, String cpu_max_freq){
        float freq     = (float) Integer.valueOf(cur_freq) / (1000 * 1000);
        float min_freq = (float) Integer.valueOf(cpu_min_freq) / (1000 * 1000);
        float max_freq = (float) Integer.valueOf(cpu_max_freq) / (1000 * 1000);
        float percent  = (float) (freq - min_freq) / (max_freq - min_freq);

        return percent * 100;
    }

    /*
     * Get file list of the pattern
     * /sys/devices/system/cpu/cpu[0..9]
     */
    private File[] getCPUs(){
        class CpuFilter implements FileFilter {
            @Override
            public boolean accept(File pathname) {
                if(Pattern.matches("cpu[0-9]+", pathname.getName())) {
                    return true;
                }
                return false;
            }
        }

        File dir = new File("/sys/devices/system/cpu/");
        File[] files = dir.listFiles(new CpuFilter());
        return files;
    }

    /*
     * Run the 'cat' command to read the file 'f' for the frequencies
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
            e.printStackTrace();
            return "Something Wrong with the command";
        }
    }

}
