package com.example.batteryapp;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.Date;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private static TextView textSOC, textTemperature, textVoltage, textTechnology, textStatus, textHealth, textTime, textCpuUsage;
    private static Button btnReadCpuFreq, btnSave, btnLoad;
    private static ProgressBar barCPU;

    private static TextView textWifi, textData, textBluetooth, textBrightness, textRAM, mEditText, textTemp;

    private final Battery_Receiver myBroadcast  = new Battery_Receiver();
    private final CPU_Info         myCPUInfo    = new CPU_Info();
    private final Other_Stats      myOtherStats = new Other_Stats(this);

    Intent myServiceIntent;
    private MyService myService;

    /* Called when the activity is first created. */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);

        myService = new MyService();
        myServiceIntent = new Intent(this, myService.getClass());
        if (!isMyServiceRunning(myService.getClass())) {
            startService(myServiceIntent);
        }

        initializeComponents();
        // registerBatteryLevelReceiver();

        myOtherStats.getNetworkConnectivity();
        myOtherStats.getBluetoothConnectivity();
        myOtherStats.getBrightness();
        myOtherStats.getAvailableRAM();

        // CPU Freq
        btnReadCpuFreq.setOnClickListener( this );
        btnSave.setOnClickListener( this );
        btnLoad.setOnClickListener( this );




    }

    private boolean isMyServiceRunning(Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                Log.i ("Service status", "Running");
                return true;
            }
        }
        Log.i ("Service status", "Not running");
        return false;
    }

    @Override
    public void onClick(View v) {
        if (v == btnReadCpuFreq){
            setCPUbar( (int) myCPUInfo.readCpuFreqNow() );
        } else if (v == btnSave) {
            saveFile();
        } else if (v == btnLoad) {
            loadFile();
        }
    }


    @Override
    protected void onStart() {
        super.onStart();
        System.out.println("Inside onStart");
    }

    @Override
    protected void onResume() {
        super.onResume();
        System.out.println("Inside Resume");
        registerBatteryLevelReceiver();
        btnReadCpuFreq.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                setCPUbar( (int) myCPUInfo.readCpuFreqNow() );
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
        stopService(myServiceIntent);
    }

    /* Register Battery receiver with intent filter */
    private void registerBatteryLevelReceiver() {
        // To know which intent to catch. 'ACTION_BATTERY_CHANGED'
        IntentFilter batteryLevelFilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        registerReceiver(myBroadcast, batteryLevelFilter);
    }

    /* Unregister Battery receiver */
    private void unregisterBatteryLevelReceiver() {
        try {
            unregisterReceiver(myBroadcast);
        }
        catch (Exception e){
            System.out.println("Receiver already unregistered!");
        }
    }

    /* Create a file based on timestamp */
    private void saveFile() {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss");
        String todayDate = dateFormat.format(new Date());

        String FILE_NAME = todayDate + ".txt";
        String text = "I' am a test file";
        FileOutputStream fos = null;
        try {
            fos = openFileOutput(FILE_NAME, MODE_PRIVATE);
            fos.write(text.getBytes());

            Toast.makeText( this, "Saved to " + getFilesDir() + "/" + FILE_NAME, Toast.LENGTH_LONG).show();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (fos != null) {
                try {
                    fos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    /* Read the files from internal storage and then delete them!*/
    private void loadFile() {
        FileInputStream fis = null;
        String[] files = fileList();
        for (int i = 0; i < files.length; i++) {
            System.out.println(files[i]);
        }
        for (String FILE_NAME : files) {
            try {
                fis = openFileInput(FILE_NAME);
                InputStreamReader isr = new InputStreamReader(fis);
                BufferedReader br = new BufferedReader(isr);
                StringBuilder sb = new StringBuilder();
                String text;

                while ((text = br.readLine()) != null) {
                    sb.append(text).append("\n");
                }

                mEditText.setText(sb.toString());
                deleteFile(FILE_NAME);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                if (fis != null) {
                    try {
                        fis.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }

    /* Buttons, TextViews, ProgressBars are initialized here */
    private void initializeComponents(){
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
        btnSave         = (Button) findViewById(R.id.btnSave);
        btnLoad         = (Button) findViewById(R.id.btnLoad);
        mEditText       = (TextView) findViewById(R.id.textView);
        textTemp        = (TextView) findViewById(R.id.textTemp);

    }

    /* Set text of the Text Views */
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
    public void setAvailableRam(String text) {
        textRAM.setText(text);
    }
    public void setBrightness(String text) {
        textBrightness.setText(text);
    }
    public void setBluetoothConnectivity(String text, int color) {
        textBluetooth.setText(text);
        textBluetooth.setTextColor(color);
    }
    public void setWiFiConnectivity(String text, int color) {
        textWifi.setText(text);
        textWifi.setTextColor(color);
    }
    public void setCellularConnectivity(String text, int color) {
        textData.setText(text);
        textData.setTextColor(color);
    }

    public void setCPUbar(int usage) {
        barCPU.setProgress(usage);
        setCPUUsage(usage);
        System.out.println(usage);
    }

    public void setCPUUsage(int usage) { textCpuUsage.setText("CPU Usage Estimation: " + usage + "%"); }

    public void setTempText(String text) {
        textTemp.setText(text);
    }

}