package com.example.batteryapp;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ActivityManager;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
import java.text.DecimalFormat;
import java.util.Timer;
import java.util.TimerTask;
import java.util.regex.Pattern;

public class MainActivity extends AppCompatActivity {
    private static TextView textSOC, textTemperature, textVoltage, textRAM, textBrightness, textTemp;
    private static TextView textTechnology, textStatus, textHealth, textTime, textCpuUsage;
    private static Button btnReadCpuFreq;
    private static ProgressBar barCPU;

    private static TextView textWifi, textData, textBluetooth;
    private static boolean wifiConnected = false;   // Whether there is a Wi-Fi connection.
    private static boolean mobileConnected = false; // Whether there is a mobile connection.

    private final Battery_Receiver myBroadcast = new Battery_Receiver();
    private final int MB_CONVERTION = 1024*1024;
    private static DecimalFormat df = new DecimalFormat("0.00");

    /* Called when the activity is first created. */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);
        textSOC         = (TextView) findViewById(R.id.batteryLevel);
        textTemperature = (TextView) findViewById(R.id.batteryTemperature);
        textVoltage     = (TextView) findViewById(R.id.batteryVoltage);
        textTechnology  = (TextView) findViewById(R.id.batteryTechnology);
        textStatus      = (TextView) findViewById(R.id.batteryStatus);
        textHealth      = (TextView) findViewById(R.id.batteryHealth);
        textTime        = (TextView) findViewById(R.id.updateTime);

        textWifi        = (TextView) findViewById(R.id.wifiStatus);
        textData        = (TextView) findViewById(R.id.dataStatus);
        textBluetooth   = (TextView) findViewById(R.id.bluetoothStatus);

        textRAM         = (TextView) findViewById(R.id.ramUsage);
        textBrightness  = (TextView) findViewById(R.id.textBright);
        textCpuUsage    = (TextView) findViewById(R.id.cpuUsage);
        barCPU          = (ProgressBar) findViewById(R.id.barCPU);
        btnReadCpuFreq  = (Button) findViewById(R.id.btnCPU);
        textTemp        = (TextView) findViewById(R.id.temp);
        // registerBatteryLevelReceiver();

        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();
        if (activeInfo != null && activeInfo.isConnected()) {
            wifiConnected = activeInfo.getType() == ConnectivityManager.TYPE_WIFI;
            mobileConnected = activeInfo.getType() == ConnectivityManager.TYPE_MOBILE;
        } else {
            wifiConnected = false;
            mobileConnected = false;
        }
        if (wifiConnected) {
            textWifi.setText("WiFI Enable");
            textWifi.setTextColor(Color.GREEN);
        }
        if (mobileConnected) {
            textData.setText("Data Enable");
            textData.setTextColor(Color.GREEN);
        }
        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            textBluetooth.setText("No Bluetooth Support");
            textBluetooth.setTextColor(Color.RED);
        } else if (mBluetoothAdapter.isEnabled()){
            textBluetooth.setText("Bluetooth Enable");
            textBluetooth.setTextColor(Color.GREEN);
        }
        // Brightness
        int brightness = getScreenBrightness();
        textBrightness.setText("Current Brightness: " + brightness);

        // RAM reading
        /* refer to: https://developer.android.com/reference/android/app/ActivityManager.MemoryInfo */
        /* The total memory accessible by the kernel. This is basically the RAM size of the device,
            not including below-kernel fixed allocations like DMA buffers, RAM for the baseband CPU, etc.
            The available memory on the system. This number should not be considered absolute: due to the nature of the kernel,
            a significant portion of this memory is actually in use and needed for the overall system to run well. */
        ActivityManager.MemoryInfo myMemoryInfo = new ActivityManager.MemoryInfo();
        ActivityManager activityManager = (ActivityManager) getSystemService(ACTIVITY_SERVICE);
        activityManager.getMemoryInfo(myMemoryInfo);
        double availMemMB = (double) myMemoryInfo.availMem / MB_CONVERTION;
        //Percentage can be calculated for API 16+ ~ TotalMem return bytes, convert to MBytes.
        double totalMemMB = (double) myMemoryInfo.totalMem / MB_CONVERTION;
        double percentAvail = availMemMB / totalMemMB  * 100.0;
        textRAM.setText("Available RAM: " + df.format(availMemMB) + " MB (" + df.format(percentAvail) + "%)");

        // CPU Freq
        btnReadCpuFreq.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setCPUbar( (int) readCpuFreqNow() );
            }
        });

        /*Timer timer = new Timer();
        // Set the schedule function
        timer.scheduleAtFixedRate(new TimerTask() {
                                      @Override
                                      public void run() {
                                          setCPUbar( (int) readCpuFreqNow() );
                                      }
                                  },
                                        0, 1000);   // 1000 Millisecond  = 1 second
        */

    }

    private float readCpuFreqNow(){
        File[] cpuFiles = getCPUs(); // Get number of CPUs

        String output = "";
        float totalPercent = 0;
        String scaling_cur_freq = "";
        String cpuinfo_min_freq = "";
        String cpuinfo_max_freq = "";
        //String cpuinfo_cur_freq = "";
        for(int i = 0; i < cpuFiles.length; i++) {
            // Files to be read
            String path_scaling_cur_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/scaling_cur_freq";
            String path_cpuinfo_min_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/cpuinfo_min_freq";
            String path_cpuinfo_max_freq =
                    cpuFiles[i].getAbsolutePath() + "/cpufreq/cpuinfo_max_freq";
            //String path_cpu_cur_freq =
            //        cpuFiles[i].getAbsolutePath() + "/cpufreq/cpuinfo_cur_freq";
            // Commands to be executed //
            scaling_cur_freq = cmdCat(path_scaling_cur_freq);
            cpuinfo_min_freq = cmdCat(path_cpuinfo_min_freq);
            cpuinfo_max_freq = cmdCat(path_cpuinfo_max_freq);

            //cpuinfo_cur_freq = cmdCat(path_cpu_cur_freq);
            //System.out.println("Curr freq: " + cpuinfo_cur_freq);
            scaling_cur_freq = ( scaling_cur_freq.equals("") ) ? "0" : scaling_cur_freq;
            cpuinfo_min_freq = ( cpuinfo_min_freq.equals("") ) ? "0" : cpuinfo_min_freq;
            cpuinfo_max_freq = ( cpuinfo_max_freq.equals("") ) ? "0" : cpuinfo_max_freq;

            output = output + myFormat(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            totalPercent += getUsage(scaling_cur_freq, cpuinfo_min_freq, cpuinfo_max_freq);
            System.out.println(totalPercent);
            output = ( (i % 2) != 0) ? output + "\n" : output + " | " ;
        }
        textTemp.setText(output);
        System.out.println(cpuFiles.length);
        return totalPercent / cpuFiles.length;
    }
    private String myFormat(String cur_freq, String cpu_min_freq, String cpu_max_freq){
        float freq = (float) Integer.valueOf(cur_freq) / (1000 * 1000);
        float min_freq = (float) Integer.valueOf(cpu_min_freq) / (1000 * 1000);
        float max_freq = (float) Integer.valueOf(cpu_max_freq) / (1000 * 1000);
        String currFormat = String.format( "%s [%s - %s]", df.format(freq), df.format(min_freq), df.format(max_freq));
        return currFormat;
    }


    /*Format my output as curr_freq [min - max] */
    private float getUsage(String cur_freq, String cpu_min_freq, String cpu_max_freq){
        float freq = (float) Integer.valueOf(cur_freq) / (1000 * 1000);
        float min_freq = (float) Integer.valueOf(cpu_min_freq) / (1000 * 1000);
        float max_freq = (float) Integer.valueOf(cpu_max_freq) / (1000 * 1000);
        float percent  = (float) (freq - min_freq) / (max_freq - min_freq);
        System.out.println( String.format( "%f [%f - %f]", freq, min_freq, max_freq) );
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

    //run Linux command ~ cat f
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

    @Override
    protected void onResume() {
        super.onResume();
        System.out.println("Inside Resume");
        registerBatteryLevelReceiver();
        btnReadCpuFreq.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //System.out.println("Temp cpu is: " + cmdCat("/sys/devices/system/cpu/cpu0/cpufreq/cpu_temp"));
                //System.out.println("Governor is: " + cmdCat("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"));
                setCPUbar( (int) readCpuFreqNow() );
            }
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        System.out.println("Inside Pause");
        unregisterBatteryLevelReceiver();
    }

    @Override
    protected void onStop() {
        super.onStop();
        System.out.println("Inside Stop");
        unregisterBatteryLevelReceiver();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("Inside Destroy");
        unregisterBatteryLevelReceiver();
    }

    //Register Battery receiver with intent filter
    private void registerBatteryLevelReceiver() {
        // To know which intent to catch. 'ACTION_BATTERY_CHANGED'
        IntentFilter batteryLevelFilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        registerReceiver(myBroadcast, batteryLevelFilter);
    }

    //Unregister Battery receiver
    private void unregisterBatteryLevelReceiver() {
        try {
            unregisterReceiver(myBroadcast);
        }
        catch (Exception e){
            System.out.println("Receiver already unregistered!");
        }
    }

    // Get the screen current brightness
    protected int getScreenBrightness(){
        int brightnessValue = Settings.System.getInt(
                getApplicationContext().getContentResolver(),
                Settings.System.SCREEN_BRIGHTNESS,
                0
        );
        return brightnessValue;
    }

    //Set text of the Text Views
    public void setBatteryLevel(String text) {
        textSOC.setText(text);
    }
    public void setBatteryTemp(String text) {
        textTemperature.setText(text);
    }
    public void setBatteryVolt(String text) {
        textVoltage.setText(text);
    }
    public void setBatteryTech(String text) {
        textTechnology.setText(text);
    }
    public void setBatteryStatus(String text) {
        textStatus.setText(text);
    }
    public void setBatteryHealth(String text) {
        textHealth.setText(text);
    }
    public void setUpdateTime(String text) {
        textTime.setText(text);
    }
    public void setCPUbar(int usage) {
        barCPU.setProgress(usage);
        setCPUUsage(usage);
        System.out.println(usage);
    }
    public void setCPUUsage(int usage) { textCpuUsage.setText("CPU Usage Estimation: " + usage + "%"); }

}