package com.example.batteryapp;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.Scanner;
import java.util.UUID;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import okio.Buffer;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private static TextView textSOC, textTemperature, textVoltage, textTechnology, textStatus, textHealth, textTime, textCpuUsage;
    private static FloatingActionButton btnUpload;
    private static ProgressBar barCPU;
    private static TextView textWifi, textData, textBluetooth, textBrightness, textRAM, mEditText, textUUID;

    private static String userID;
    private IOHelper myIOHelper;
    public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    Intent myServiceIntent;
    private MyService myService;

    /* Called when the activity is first created. */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);
        initializeComponents();

        myIOHelper = new IOHelper(this);

        /* Create a unique id per user, only for the 1st time */
        File f = new File(getFilesDir() + "/UUID.txt");
        if (!f.exists()) {
            // The first time create the file to store the ID
            userID = UUID.randomUUID().toString();
            userID = userID.replace("-", "");
            setTextUUID("Your Unique userID is: " + userID);
            myIOHelper.saveFile(userID, "UUID.txt");
        } else {
            try {
                Scanner myReader = new Scanner(f);
                while (myReader.hasNextLine()) {
                    userID = myReader.nextLine();
                }
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

        // File upload
        btnUpload.setOnClickListener(this);

    }

    private boolean isMyServiceRunning(Class<?> serviceClass) {
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                Log.i("Service status", "Running");
                return true;
            }
        }
        Log.i("Service status", "Not running");
        return false;
    }

    @Override
    public void onClick(View v) {
        if (v == btnUpload) {
            String[] files = fileList();
            for (String FILE_NAME : files) {
                if (!FILE_NAME.contains("UUID")) {
                    System.out.println(FILE_NAME);
                    String json = myIOHelper.loadFile(FILE_NAME);

                    OkHttpAsync okHttpAsync = new OkHttpAsync();
                    okHttpAsync.execute("http://192.168.100.4:5000/postjson", json, FILE_NAME);

                }
            }
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
    }

    @Override
    protected void onPause() {
        super.onPause();
        System.out.println("Inside Pause");
    }

    @Override
    protected void onStop() {
        super.onStop();
        System.out.println("Inside Stop");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("Inside Destroy of Activity. Calling StopService ...");

        stopService(myServiceIntent);
        // myService.onDestroy();
    }

    /* Buttons, TextViews, ProgressBars are initialized here */
    private void initializeComponents() {
        textSOC = (TextView) findViewById(R.id.batteryLevel);
        textTemperature = (TextView) findViewById(R.id.batteryTemperature);
        textVoltage = (TextView) findViewById(R.id.batteryVoltage);
        textTechnology = (TextView) findViewById(R.id.batteryTechnology);
        textStatus = (TextView) findViewById(R.id.batteryStatus);
        textHealth = (TextView) findViewById(R.id.batteryHealth);
        textTime = (TextView) findViewById(R.id.updateTime);

        textWifi = (TextView) findViewById(R.id.wifiStatus);
        textData = (TextView) findViewById(R.id.dataStatus);
        textBluetooth = (TextView) findViewById(R.id.bluetoothStatus);

        textRAM = (TextView) findViewById(R.id.ramUsage);
        textBrightness = (TextView) findViewById(R.id.textBright);
        textCpuUsage = (TextView) findViewById(R.id.cpuUsage);
        barCPU = (ProgressBar) findViewById(R.id.barCPU);
        btnUpload = (FloatingActionButton) findViewById(R.id.btnUpload);
        mEditText = (TextView) findViewById(R.id.textView);
        textUUID = (TextView) findViewById(R.id.UserID);

    }

    public String getUUID() {
        return userID;
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
    }

    public void setCPUUsage(int usage) {
        textCpuUsage.setText("CPU Usage Estimation: " + usage + "%");
    }

    public void setTextUUID(String text) {
        textUUID.setText(text);
    }

    public class OkHttpAsync extends AsyncTask<String, Void, String> {

        private OkHttpClient myClient;

        @Override
        protected String doInBackground(String... params) {
            myClient = new OkHttpClient();
            int postCode;
            try {
                RequestBody body = RequestBody.create(JSON, params[1]);
                Request request = new Request.Builder()
                        .header("name", params[2])
                        .url(params[0])
                        .post(body)
                        .build();
                /* Debug Purposes for the response
                final Buffer buffer = new Buffer();
                body.writeTo(buffer);
                System.out.println(buffer.readUtf8()); */
                Response response = myClient.newCall(request).execute();
                postCode = response.code();
                /* Without it, i get a warning: W/System.out: A resource failed to call response.body().close(). */
                response.body().close();

                //System.out.println(postCode);
                if (postCode == 200) {
                    /* Delete the file until now. If the app don't close immediately, the remaining json files will be written the next time */
                    deleteFile(params[2]);
                    return "File Upload Successfully";
                } else {
                    return "Something went wrong. Try again later.";
                }
            } catch (IOException e) {
                System.out.println(e.toString());
                String exceptionName = e.getClass().getCanonicalName();
                return exceptionName + ". Try again later.";
                // return e.toString();
            }
        }

        @Override
        protected void onPostExecute(String message) {
            /* Handle result here */
            Toast.makeText(getApplicationContext(), message, Toast.LENGTH_LONG).show();
        }

        /* post request code here
        int doPostRequest(String url, String json, String filename) throws IOException {
            RequestBody body = RequestBody.create(JSON, json);
            Request request = new Request.Builder()
                    .header("name", filename)
                    .url(url)
                    .post(body)
                    .build();
            /* Debug Purposes for the response
            final Buffer buffer = new Buffer();
            body.writeTo(buffer);
            System.out.println(buffer.readUtf8());
        Response response = myClient.newCall(request).execute();
        // response.body().close();
            return response.code();
    }*/
    }
}
