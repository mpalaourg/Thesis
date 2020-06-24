package com.example.batteryapp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private static TextView textSOC, textTemperature, textVoltage, textTechnology, textStatus, textHealth, textTime, textCpuUsage;
    private static Button btnReadCpuFreq, btnStartService, btnStopService;
    private static ProgressBar barCPU;

    private static TextView textWifi, textData, textBluetooth, textBrightness, textRAM;

    private final Battery_Receiver myBroadcast  = new Battery_Receiver();
    private final CPU_Info         myCPUInfo    = new CPU_Info();
    private final Other_Stats      myOtherStats = new Other_Stats(this);

    /* Called when the activity is first created. */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);

        initializeComponents();
        // registerBatteryLevelReceiver();

        myOtherStats.getNetworkConnectivity();
        myOtherStats.getBluetoothConnectivity();
        myOtherStats.getBrightness();
        myOtherStats.getAvailableRAM();

        btnStartService.setOnClickListener( this );
        btnStopService.setOnClickListener( this );

        // CPU Freq
        btnReadCpuFreq.setOnClickListener( this );
    }

    @Override
    public void onClick(View v) {
        if (v == btnStartService){
            startService( new Intent( this, MyService.class ));
        } else if (v == btnStopService){
            stopService( new Intent( this, MyService.class ));
        } else if (v == btnReadCpuFreq){
            setCPUbar( (int) myCPUInfo.readCpuFreqNow() );
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

        btnStartService = (Button) findViewById(R.id.btnService);
        btnStopService = (Button) findViewById(R.id.btnStopService);
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

}