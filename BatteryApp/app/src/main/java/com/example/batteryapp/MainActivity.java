package com.example.batteryapp;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ActivityManager;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Scanner;
import java.util.UUID;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private static TextView textSOC, textTemperature, textVoltage, textTechnology, textStatus, textHealth, textTime, textCpuUsage;
    private static Button btnSave, btnLoad;
    private static ProgressBar barCPU;

    private static TextView textWifi, textData, textBluetooth, textBrightness, textRAM, mEditText, textTemp, textUUID;

    private final CPU_Info         myCPUInfo    = new CPU_Info();
    private static String          userID;

    Intent myServiceIntent;
    private MyService myService;
    /* Called when the activity is first created. */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);
        initializeComponents();

        /* Create a unique id per user, only for the 1st time */
        File f = new File(getFilesDir() + "/UUID.txt");
        if ( !f.exists() ) {
            // The first time create the file to store the ID
            userID = UUID.randomUUID().toString();
            userID = userID.replace("-", "");
            setTextUUID("Your Unique userID is: " + userID);
            saveFile(userID,"UUID.txt");
        } else {
            try {
                Scanner myReader = new Scanner(f);
                while (myReader.hasNextLine()) { userID = myReader.nextLine(); }
                myReader.close();
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            setTextUUID("Your Unique userID is: " + userID);
        }

        myService = new MyService();
        myServiceIntent = new Intent(this, myService.getClass());
        if (!isMyServiceRunning(myService.getClass())) {
            startService(myServiceIntent);
        }


        // CPU Freq
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
        if (v == btnSave) {
            SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss");
            String todayDate = dateFormat.format(new Date());

            String FILE_NAME = todayDate + ".txt";
            saveFile("This is a test file", FILE_NAME);
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
        //registerBatteryLevelReceiver();
    }

    @Override
    protected void onPause() {
        super.onPause();
        System.out.println("Inside Pause");
        //unregisterBatteryLevelReceiver();
    }

    @Override
    protected void onStop() {
        super.onStop();
        System.out.println("Inside Stop");
      //  unregisterBatteryLevelReceiver();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("Inside Destroy of Activity. Calling StopService ...");

        stopService(myServiceIntent);
        // myService.onDestroy();
    }

    /* Create a file with name "FILE_NAME" that contains "text" */
    private void saveFile(String text, String FILE_NAME) {
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
            if ( !FILE_NAME.contains("UUID")) {
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
        btnSave         = (Button) findViewById(R.id.btnSave);
        btnLoad         = (Button) findViewById(R.id.btnLoad);
        mEditText       = (TextView) findViewById(R.id.textView);
        textTemp        = (TextView) findViewById(R.id.textTemp);
        textUUID        = (TextView) findViewById(R.id.UserID);

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

    public void setTextUUID(String text) {
        textUUID.setText(text);
    }
    public void setTempText(String text) {
        textTemp.setText(text);
    }

}