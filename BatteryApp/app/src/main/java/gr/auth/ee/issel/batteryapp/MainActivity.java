package gr.auth.ee.issel.batteryapp;

import android.app.ActivityManager;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Switch;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import gr.auth.ee.issel.batteryapp.R;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import java.util.Scanner;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity implements View.OnClickListener {
    private TextView textSOC, textTemperature, textVoltage, textTechnology, textStatus, textHealth, textTime;
    private FloatingActionButton btnUpload;
    private ProgressBar barCPU;
    private TextView textWifi, textData, textBluetooth, textBrightness, textRAM, textUUID, textCpuUsage, textFiles;
    private EditText textSampleFreq;
    private Button btnSubmit, btnStartSession, btnEndSession;
    private Switch switchWiFiUpload;

    private static String userID, FILE_NAME;
    private static DecimalFormat df = new DecimalFormat("0.00");

    private int sampleFreq;
    private IOHelper myIOHelper;
    public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    Intent myServiceIntent;
    private MyService myService;
    private BroadcastReceiver receiver;
    private ArrayList<OkHttpAsync> AsyncTasksList;
    private boolean UPLOAD_VIA_WIFI_ONLY = true;
    private long lastClickTime = 0;

    /* Called when the activity is first created. */

    /**
     * This method will be called on the creation of the activity. First, the UI components will be
     * initialized. Only for the installation, a unique user ID (and file) will be created. Then, a
     * file associated with the current session will be created (based on UUID and the current time).
     * Finally, a service will be started with a default Sampling Frequency of 10 seconds and the
     * listeners for the buttons will be set
     * @param savedInstanceState ->  If the activity is being re-initialized after previously being shut down then this Bundle contains the data
     *                               it most recently supplied in onSaveInstanceState(Bundle). Otherwise it is null.
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("Inside Create");
        setContentView(R.layout.activity_main);
        myIOHelper = new IOHelper(this);
        AsyncTasksList = new ArrayList<>();
        initializeComponents();

        /* Create a unique id per user, only for the 1st time */
        File f = new File(getFilesDir() + "/UUID.txt");
        if (!f.exists()) {
            // The first time create the file to store the ID
            userID = UUID.randomUUID().toString();
            userID = userID.replace("-", "");
            setTextUUID("Your Unique userID is: " + userID);
            myIOHelper.saveFile("UUID.txt", userID);
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

        scheduleNotification();
        /* Create the file for the current use */
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.getDefault());
        String todayDate = dateFormat.format(new Date());
        FILE_NAME = userID + "-" + todayDate;
        myIOHelper.saveFile(FILE_NAME, "");

        /* By default sampling frequency is 10 seconds */
        sampleFreq = 10;
        myService = new MyService();
        myServiceIntent = new Intent(this, myService.getClass());
        /* Pass the arguments to the service */
        myServiceIntent.putExtra("SampleFreq", sampleFreq);
        myServiceIntent.putExtra("FILENAME", FILE_NAME);
        myServiceIntent.putExtra("userID", userID);
        if (!isMyServiceRunning(myService.getClass())) {
            startService(myServiceIntent);
        }

        btnUpload.setOnClickListener(this); /* File upload */
        btnSubmit.setOnClickListener(this); /* Change Sampling Frequency */
        btnStartSession.setOnClickListener(this); /* Start the Session - Minimize the app */
        btnEndSession.setOnClickListener(this); /* End the Session - Close the app */

        switchWiFiUpload.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                UPLOAD_VIA_WIFI_ONLY = isChecked;
            }
        });

        updateTextFiles();
    }

    /**
     * Check if a service is already running or a new one must be initialized.
     * @param serviceClass The class of the service to be checked.
     * @return true if a service is already running (boolean)
     */
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

    /**
     * The methods to be called on the buttons clicks.
     *  btnUpload: First will check if a Wifi Connection is enable. If WiFi connection is established
     *             then an AsyncTask will be created (for each file) to upload to the url, the json
     *             content provided, with the proper FILE_NAME.
     *  btnSubmit: The user wants to change the sampling frequency. First, the input will be checked
     *             to be between the proper boundaries. If true, the previous service will be cleared
     *             and a new one will be schedule to sample with the new Sampling Frequency. Finally,
     *             the keyboard will be closed and the ediText will be cleared and ready for the next
     *             user input.
     * @param v -> View: The view (Button) that was clicked.
     */
    @Override
    public void onClick(View v) {
        if (v == btnUpload) {
            if (SystemClock.elapsedRealtime() - lastClickTime < 8000){ return; }    // Double click
            lastClickTime = SystemClock.elapsedRealtime();
            boolean WiFiConnected = false;
            boolean CellularConnected = false;
            ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();
            if (!UPLOAD_VIA_WIFI_ONLY) {
                if (activeInfo != null && activeInfo.isConnected()) { CellularConnected = activeInfo.getType() == ConnectivityManager.TYPE_MOBILE; }
            }
            if (activeInfo != null && activeInfo.isConnected()) { WiFiConnected = activeInfo.getType() == ConnectivityManager.TYPE_WIFI; }
            if (WiFiConnected || CellularConnected) {
                String[] files = fileList();
                if (files.length == 1) { ToastManager.showToast(this, "Nothing to upload!"); }
                for (String FILE_NAME : files) {
                    // System.out.println("Outside if: " + FILE_NAME);
                    if (!FILE_NAME.contains("UUID")) {
                        // System.out.println(FILE_NAME);
                        String json = myIOHelper.loadFile(FILE_NAME);
                        /* Just like threads, AsyncTasks can't be reused. You have to create a new instance every time you want to run one.
                            Ref link: https://stackoverflow.com/a/6879803 */
                        OkHttpAsync okHttpAsync = new OkHttpAsync(this);
                        AsyncTasksList.add(okHttpAsync);
                        //okHttpAsync.execute("http://hostmpalaourgthesis.ddns.net:5000/postjson", json, FILE_NAME);
                        okHttpAsync.execute("http://83.212.110.253:5000/postjson", json, FILE_NAME);
                    }
                }
            } else {
                if (UPLOAD_VIA_WIFI_ONLY) { ToastManager.showToast(this, "WiFi is Disabled. Upload only via WiFi."); }
                else { ToastManager.showToast(this, "No internet Connection"); }
            }
        } else if (v == btnSubmit){
            String userInput = textSampleFreq.getText().toString();
            if (!userInput.equals("")) {
                int tempInput = (int) Double.parseDouble(userInput);
                if (tempInput < 5) {
                    textSampleFreq.setError("Sampling frequency must be equal or greater than 5.");
                } else if (tempInput > 10) {
                    textSampleFreq.setError("Sampling frequency must be equal or less than 10.");
                } else {
                    sampleFreq = tempInput;
                    ToastManager.showToast(this, "Your current Sampling Frequency is: " + sampleFreq + " seconds.");
                    textSampleFreq.setHint("Current is " + sampleFreq + " seconds.");
                    /* Stop the previous service and start a new one */
                    stopService(myServiceIntent);
                    myServiceIntent = new Intent(this, myService.getClass());
                    myServiceIntent.putExtra("SampleFreq", sampleFreq);
                    myServiceIntent.putExtra("FILENAME", FILE_NAME);
                    myServiceIntent.putExtra("userID", userID);
                    if (!isMyServiceRunning(myService.getClass())) {
                        startService(myServiceIntent);
                    }
                }
            }
            InputMethodManager inputManager = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            View view = getCurrentFocus();
            if (view != null) { inputManager.hideSoftInputFromWindow(view.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS); }
            textSampleFreq.setText("");
            textSampleFreq.clearFocus();
        } else if (v == btnStartSession){
            btnStartSession.setText(R.string.TextResumeSession);
            Intent startMain = new Intent(Intent.ACTION_MAIN);
            startMain.addCategory(Intent.CATEGORY_HOME);
            startMain.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(startMain);
        } else if (v == btnEndSession){
            finish();
        }
    }

    /**
     * The method will be called on the start of the activity. A receiver will be created, for
     * updating the UI Thread, when a new sample will be collected by the Service. Finally, register
     * the receiver to wait for a "UpdateIntent" intent.
     */
    @Override
    protected void onStart() {
        super.onStart();
        System.out.println("Inside onStart");
        receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                boolean wifi      = intent.getBooleanExtra("WiFiConnectivity", false);
                boolean cellular  = intent.getBooleanExtra("CellularConnectivity", false);
                boolean bluetooth = intent.getBooleanExtra("BluetoothConnectivity", false);
                double RAM        = intent.getDoubleExtra("AvailableRAM", 0);
                int brightness    = intent.getIntExtra("Brightness", 0);
                int usage         = intent.getIntExtra("CPU", 0);

                int level         = intent.getIntExtra("BatteryLevel", -1);
                String status     = intent.getStringExtra("BatteryStatus");
                String health     = intent.getStringExtra("BatteryHealth");
                float temperature = intent.getFloatExtra("BatteryTemp", 0.0f);
                float voltage     = intent.getFloatExtra("BatteryVolt", 0.0f);
                String technology = intent.getStringExtra("BatteryTech");
                String date       = intent.getStringExtra("BatteryUpdateDate");

                if (wifi){
                    setWiFiConnectivity("WiFI Enable", Color.GREEN);
                    setCellularConnectivity("Data Disable", Color.BLACK);
                }else if (cellular){
                    setWiFiConnectivity("WiFI Disable", Color.BLACK);
                    setCellularConnectivity("Data Enable", Color.GREEN);
                } else {
                    setWiFiConnectivity("WiFI Disable", Color.BLACK);
                    setCellularConnectivity("Data Disable", Color.BLACK);
                }
                if (bluetooth){
                    setBluetoothConnectivity("Bluetooth Enable", Color.GREEN);
                } else {
                    setBluetoothConnectivity("Bluetooth Disable", Color.BLACK);
                }
                setProgressBarCPU(usage);
                setTextCPU("CPU Usage Estimation: " + usage + "%");
                setAvailableRam("Available RAM: " + df.format(RAM) + "%");
                setBrightness("Current Brightness: " + brightness);

                setBatteryLevel("Battery Level Remaining: " + level + "%");
                setBatteryStatus("Battery Status: " + status);
                setBatteryHealth("Battery Health: " + health);
                setBatteryTemp("Battery Temperature: " + temperature+ " \u00B0" + "C");
                setBatteryVolt("Battery Voltage: " + voltage + " V");
                setBatteryTech("Battery Technology: " + technology);
                setUpdateTime("Last Updated: " + date);
                updateTextFiles();
            }
        };

        LocalBroadcastManager.getInstance(this).registerReceiver( (receiver), new IntentFilter("UpdateIntent"));
    }

    @Override
    protected void onResume() {
        super.onResume();
        System.out.println("Inside Resume");
        // updateUI() Unregister the receiver onDestroy
    }

    @Override
    protected void onPause() {
        super.onPause();
        System.out.println("Inside Pause");
        btnStartSession.setText(R.string.TextResumeSession);
    }

    /**
     * The method will be called when the user exit or minimize the activity. The UI thread doesn't
     * need to be updated during this time, so the receiver will be unregistered from the "UpdateIntent"
     * intent.
     */
    @Override
    protected void onStop() {
        super.onStop();
        System.out.println("Inside Stop");
        /* If i unregister at onDestroy i will get rid of N/A after closed phone opening the app and missing intents */
        LocalBroadcastManager.getInstance(this).unregisterReceiver(receiver);
        ToastManager.dismissToast();
        for (int i = 0; i < AsyncTasksList.size(); i++) {
            /* Calling this method will result in onCancelled(Object) being invoked on the UI thread
               after doInBackground(Object[]) returns. Calling this method guarantees that onPostExecute(Object)
               is never subsequently invoked, even if cancel returns false, but onPostExecute has not yet run.  */
            AsyncTasksList.get(i).cancel(true);
        }
    }

    /**
     * This method will be called when the user exit the activity (press the back button). The service
     * is no longer needed it, so it will be stopped with stopService().
     */
    @Override
    protected void onDestroy() {
        super.onDestroy();
        System.out.println("Inside Destroy of Activity. Calling StopService ...");
        stopService(myServiceIntent);
    }

    /**
     * This method will count the number of files -minus the UUID.txt- and set the
     * text to show the appropriate message for the user.
     */
    private void updateTextFiles() {
        String[] files = fileList();
        String text;
        int numberOfFiles = files.length - 1;   // Without the UUID.txt
        if (numberOfFiles == 0){
            text = "Nothing to upload!";
        } else if (numberOfFiles == 1){
            text = "You only have the current file ready for upload.";
        } else {
            text = "You have " + numberOfFiles + " files ready for upload.";
        }
        setTextFiles(text);
    }

    /**
     * Schedule a notification in 24 hours from when the user last use the app.
     */
    public void scheduleNotification() {
        Intent alarmIntent = new Intent(MainActivity.this, AlarmReceiver.class);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(MainActivity.this, 0, alarmIntent, PendingIntent.FLAG_UPDATE_CURRENT);
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        Calendar calendar = Calendar.getInstance();

        calendar.add(Calendar.DATE, 1); long repeat = 1 * 24 * 60 * 60 * 1000;
        // calendar.add(Calendar.HOUR, 12); long repeat = 12 * 60 * 60 * 1000;
        // calendar.add(Calendar.HOUR, 6); long repeat = 6 * 60 * 60 * 1000;
        manager.setInexactRepeating(AlarmManager.RTC_WAKEUP, calendar.getTimeInMillis(), repeat, pendingIntent);
    }

    /* private members of the Main Activity and call them to update the UI */
    /* private void updateUI() {
        if (wifi){
            setWiFiConnectivity("WiFI Enable", Color.GREEN);
            setCellularConnectivity("Data Disable", Color.BLACK);
        }else if (cellular){
            setWiFiConnectivity("WiFI Disable", Color.BLACK);
            setCellularConnectivity("Data Enable", Color.GREEN);
        } else {
            setWiFiConnectivity("WiFI Disable", Color.BLACK);
            setCellularConnectivity("Data Disable", Color.BLACK);
        }
        if (bluetooth){
            setBluetoothConnectivity("Bluetooth Enable", Color.GREEN);
        } else {
            setBluetoothConnectivity("Bluetooth Disable", Color.BLACK);
        }
        setProgressBarCPU(usage);
        setTextCPU("CPU Usage Estimation: " + usage + "%");
        setAvailableRam("Available RAM: " + df.format(RAM) + "%");
        setBrightness("Current Brightness: " + brightness);

        setBatteryLevel("Battery Level Remaining: " + level + "%");
        setBatteryStatus("Battery Status: " + status);
        setBatteryHealth("Battery Health: " + health);
        setBatteryTemp("Battery Temperature: " + temperature+ " \u00B0" + "C");
        setBatteryVolt("Battery Voltage: " + voltage + " V");
        setBatteryTech("Battery Technology: " + technology);
        setUpdateTime("Last Updated: " + date);
    } */

    /**
     * All the views (Buttons, TextViews, ProgressBar etc) of the activity will be initialized here.
     */
    private void initializeComponents() {
        textSOC         = findViewById(R.id.batteryLevel);
        textTemperature = findViewById(R.id.batteryTemperature);
        textVoltage     = findViewById(R.id.batteryVoltage);
        textTechnology  = findViewById(R.id.batteryTechnology);
        textStatus      = findViewById(R.id.batteryStatus);
        textHealth      = findViewById(R.id.batteryHealth);
        textTime        = findViewById(R.id.updateTime);

        textWifi       = findViewById(R.id.wifiStatus);
        textData       = findViewById(R.id.dataStatus);
        textBluetooth  = findViewById(R.id.bluetoothStatus);
        textRAM        = findViewById(R.id.ramUsage);
        textBrightness = findViewById(R.id.textBright);
        textCpuUsage   = findViewById(R.id.cpuUsage);
        barCPU         = findViewById(R.id.barCPU);

        btnUpload = findViewById(R.id.btnUpload);
        textUUID  = findViewById(R.id.UserID);
        textFiles = findViewById(R.id.textFiles);

        textSampleFreq  = findViewById(R.id.editTextNumber);
        btnSubmit       = findViewById(R.id.btnSubmit);
        btnStartSession = findViewById(R.id.btnStartSession);
        btnEndSession   = findViewById(R.id.btnEndSession);

        switchWiFiUpload = findViewById(R.id.switchUpload);
        switchWiFiUpload.setTextOn("Yes"); // displayed text of the Switch whenever it is in checked or on state
        switchWiFiUpload.setTextOff("No");
        switchWiFiUpload.setChecked(true);
    }

    /**
     * All the methods to set the text displayed from a TextView and the other views of the activity.
     */
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
    public void setProgressBarCPU(int usage) {
        barCPU.setProgress(usage);
    }
    public void setTextCPU(String text) {
        textCpuUsage.setText(text);
    }
    public void setTextUUID(String text) {
        textUUID.setText(text);
    }
    public void setTextFiles(String text) {
        textFiles.setText(text);
    }

    /**
     * The class responsible to upload the json to the server. A WeakReference will be used to the
     * Main activity, to be safe of Memory leaks.
     */
    private static class OkHttpAsync extends AsyncTask<String, Void, String> {

        private WeakReference<MainActivity> activityReference;
        OkHttpAsync(MainActivity context) { activityReference = new WeakReference<>(context); }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            // MainActivity activity = activityReference.get();
            // activity.btnUpload.setEnabled(false);
        }

        /**
         * The method will be called when a OkHttpAsync will be executed. At a response code of 200
         * the file being uploaded will be deleted to save some memory.
         * @param params -> A list of string parameters to be used inside the method (url | json | FILE_NAME)
         * @return A string holding the server response
         */
        @Override
        protected String doInBackground(String... params) {
            // TODO CHECK IF THE Async Task has been cancelled
            if (!isCancelled()) {
                /* Default timeouts: connectTimeout: 10 seconds, writeTimeout: 10 seconds, readTimeout: 30 seconds */
                OkHttpClient myClient = new OkHttpClient.Builder().connectTimeout(15, TimeUnit.SECONDS).build();
                MainActivity activity = activityReference.get();
                int postCode;
                try {
                    RequestBody body = RequestBody.create(JSON, params[1]);
                    Request request = new Request.Builder()
                            .header("name", params[2])
                            .url(params[0])
                            .post(body)
                            .build();
                    Response response = myClient.newCall(request).execute();
                    postCode = response.code();
                    /* Without it, i get a warning: W/System.out: A resource failed to call response.body().close(). */
                    if (response.body() != null) {
                        response.body().close();
                    }
                    // System.out.println(postCode);
                    if (postCode == 200) {
                        /* Delete the file until now. If the app don't close immediately, the remaining json files will be written the next time */
                        activity.deleteFile(params[2]);
                        return "File Upload Successfully";
                    } else if (postCode == 400) {
                        /* File either not a json, or a bad header, or only one (or less) item with empty collection */
                        activity.deleteFile(params[2]);
                        return "Bad request. Either not a json file or only one item with your json.";
                    } else if (postCode == 417){
                        /* File size is less than 648 aka damaged*/
                        activity.deleteFile(params[2]);
                        return "Something went wrong. File size too small.";
                    }
                    else {
                        return "Something went wrong. Try again later.";
                    }
                } catch (IOException e) {
                    // System.out.println(e.toString());
                    String exceptionName = e.getClass().getCanonicalName();
                    return exceptionName + ". Try again later.";
                }
            } else {
                System.out.println("Task has been cancelled");
                return "Task has been cancelled";
            }
        }

        /**
         * This method will be called after the execution of the "background" OkHttpAsync task.
         * The result will be handled here and a Toast Message will be prompted to the user
         * @param message -> A string holding the server response
         */
        @Override
        protected void onPostExecute(String message) {
            MainActivity activity = activityReference.get();
            ToastManager.showToast(activity.getApplicationContext(), message);
            if (!message.contains("Try again later")) {
                activity.updateTextFiles();
            }
            // activity.btnUpload.setEnabled(true);
        }
    }
}
