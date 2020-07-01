package com.example.batteryapp;

import android.app.ActivityManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.provider.Settings;

import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;

import java.text.DecimalFormat;
import java.util.Timer;
import java.util.TimerTask;

public class MyService extends Service {
    private MainActivity currActivity;
    private String userID, FILE_NAME;

    private Timer timer;
    private CPU_Info myCPUInfo;
    private Battery_Receiver myBroadcast ;
    private IOHelper myIOHelper;
    private PowerManager pm;
    private PowerManager.WakeLock wl;

    private int level = 0, status, health, usage;
    private float temperature = 0.0f, voltage = 0.0f;
    private String technology;
    private boolean bluetooth, wifi, cellular;
    private double   RAM;
    private int     brightness, sampleFreq;
    private long    timestamp;

    private final  int MB_CONVERSION = 1000 * 1000;
    private static boolean wifiConnected = false;   // Whether there is a Wi-Fi connection.
    private static boolean mobileConnected = false; // Whether there is a mobile connection.
    private static DecimalFormat df = new DecimalFormat("0.00");


    /** Function which is called at the creation of the Service. For androids version after O
     *  will a create a foreground service with a notification, where the proper notification channel
     *  is initialized. Otherwise, the service has a simple notification.
     */
    @Override
    public void onCreate() {
        super.onCreate();
        currActivity = new MainActivity();

        timer = new Timer();
        myCPUInfo = new CPU_Info();
        myBroadcast  = new Battery_Receiver();
        myIOHelper = new IOHelper(this);;
        pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "BatteryApp:SamplingVariablesWakelock");
        wl.acquire();

        // myIOHelper.deleteFile();
        registerBatteryLevelReceiver();

        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.O)
            startMyOwnForeground();
        else
            startForeground(1, new Notification());
    }

    /**
     *
     * @param intent  -> The Intent supplied to Context.startService(Intent), as given.
     * @param flags   -> Additional data about this start request. Value is either 0 or a combination of START_FLAG_REDELIVERY, and START_FLAG_RETRY
     * @param startId -> A unique integer representing this specific request to start.
     * @return
     */
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        sampleFreq = intent.getExtras().getInt("SampleFreq");
        userID     = intent.getExtras().getString("userID");
        FILE_NAME  = intent.getExtras().getString("FILENAME");

        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                timestamp = System.currentTimeMillis();
                usage = getCPUUsage();
                level = myBroadcast.getLevel();
                status = myBroadcast.getStatus();
                health = myBroadcast.getHealth();
                temperature = myBroadcast.getTemperature();
                voltage     = myBroadcast.getVoltage();
                technology  = myBroadcast.getTechnology();

                wifi     = getWiFiConnectivity();
                cellular = getCellularConnectivity();
                bluetooth = getBluetoothConnectivity();
                RAM = Math.round( getAvailableRAM() * 100.0) / 100.0;
                brightness = getBrightness();

                currActivity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        if (wifi){
                            currActivity.setWiFiConnectivity("WiFI Enable", Color.GREEN);
                            currActivity.setCellularConnectivity("Data Disable", Color.BLACK);
                        }else if (cellular){
                            currActivity.setWiFiConnectivity("WiFI Disable", Color.BLACK);
                            currActivity.setCellularConnectivity("Data Enable", Color.GREEN);
                        } else {
                            currActivity.setWiFiConnectivity("WiFI Disable", Color.BLACK);
                            currActivity.setCellularConnectivity("Data Disable", Color.BLACK);
                        }
                        if (bluetooth){
                            currActivity.setBluetoothConnectivity("Bluetooth Enable", Color.GREEN);
                        } else {
                            currActivity.setBluetoothConnectivity("Bluetooth Disable", Color.BLACK);
                        }
                        currActivity.setAvailableRam("Available RAM: " + df.format(RAM) + "%");
                        currActivity.setBrightness("Current Brightness: " + brightness);
                        currActivity.setCPUbar(usage); // that can be outside the runnable
                    }
                });
                String json = toJsonString(userID, level, temperature, voltage, technology, status, health, usage, bluetooth, wifi, cellular, RAM, brightness, sampleFreq, timestamp);
                System.out.println(timestamp);
                myIOHelper.saveFile(FILE_NAME, json);

            }
        }, 0, sampleFreq * 1000);
        // return START_NOT_STICKY;
        return START_STICKY;
    }

    /* In case the service is deleted or crashes some how
    @Override
    public void onDestroy() {
        isServiceRunning = false;
        super.onDestroy();
    }*/

    /** Function which is called before the Service exit and close. Clean up business must be
     * done here
     */
    @Override
    public void onDestroy() {
        System.out.println("Inside on Destroy of Service");
        unregisterBatteryLevelReceiver();
        wakelockRelease();
        timerCancel();
        stopForeground(true);
        stopSelf();
        super.onDestroy();
    }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        System.out.println("Inside on TaskRemoved of Service");
        unregisterBatteryLevelReceiver();
        wakelockRelease();
        timerCancel();
        stopForeground(true);
        stopSelf();
        super.onTaskRemoved(rootIntent);
    }

    /** Function to used if clients want to bind the service.
     * Return the communication channel to the service.
     * @param intent -> The Intent that was used to bind to this service.
     * @return null (no binding needed)
     */
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    /**
     * Function to start my own Foreground Service. At first, the channel for the notification
     * must be initialized. Then, the notification is created, with proper title, icons and an activity
     * intent, so the user can by clicking the notification to open the (already open) app.
     */
    @RequiresApi(Build.VERSION_CODES.O)
    private void startMyOwnForeground()  {
        String NOTIFICATION_CHANNEL_ID = "example.permanence";
        String channelName = "Background Service";
        NotificationChannel chan = new NotificationChannel(NOTIFICATION_CHANNEL_ID, channelName, NotificationManager.IMPORTANCE_NONE);
        chan.setLightColor(Color.BLUE);
        chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);

        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        assert manager != null;
        manager.createNotificationChannel(chan);

        Intent activityIntent = new Intent(this, MainActivity.class );
        activityIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        activityIntent.setAction(Intent.ACTION_MAIN);
        activityIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity (this, 0 , activityIntent , 0 ) ;

        Bitmap icon = BitmapFactory.decodeResource(getResources(), R.drawable.my_icon);
        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID);
        Notification notification = notificationBuilder
                .setContentTitle(getResources().getString(R.string.app_name))
                .setTicker(getResources().getString(R.string.app_name))
                .setContentText(getResources().getString(R.string.my_string))
                .setSmallIcon(R.drawable.my_icon)
                .setLargeIcon(Bitmap.createScaledBitmap(icon, 128, 170, false))
                .setContentIntent(contentIntent)
                .setAutoCancel(true)
                .setOngoing(true)
                .build();
        startForeground(2, notification);
    }

    /**
     * Function to register the Battery BroadcastReceiver with intent filter.
     */
    private void registerBatteryLevelReceiver() {
        // To know which intent to catch. 'ACTION_BATTERY_CHANGED'
        IntentFilter batteryLevelFilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        registerReceiver(myBroadcast, batteryLevelFilter);
    }

    /**
     * Function to unregister (if necessary) the Battery BroadcastReceiver.
     */
    private void unregisterBatteryLevelReceiver() {
        try {
            unregisterReceiver(myBroadcast);
        }
        catch (Exception e){
            System.out.println("Receiver already unregistered!");
        }
    }

    /**
     * Function to cancel (if necessary) the timer.
     */
    private void timerCancel() {
        try {
            timer.cancel();
            timer.purge();
        }
        catch (Exception e){
            System.out.println("Timer already cancelled!");
        }
    }

    /**
     * Function to release (if necessary) the WakeLock.
     */
    private void wakelockRelease() {
        try {
            wl.release();
        }
        catch (Exception e){
            System.out.println("WakeLock already released!");
        }
    }

    /**
     * Function to read the CPU Usage estimation.
     * @return (int) CPU Usage estimation
     */
    public int getCPUUsage() {
        int cpuUse = (int) myCPUInfo.readCpuPercentNow();
        return cpuUse;
    }

    /**
     * Check if the WiFi is enable.
     * @return (boolean) True if Wifi is Enable. False otherwise.
     */
    public boolean getWiFiConnectivity() {
        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();

        if (activeInfo != null && activeInfo.isConnected()) {
            wifiConnected = activeInfo.getType() == ConnectivityManager.TYPE_WIFI;
        } else {
            wifiConnected = false;
        }

        return wifiConnected;
    }

    /**
     * Check if the Cellular Data are enable.
     * @return (boolean) True if Cellular Data are Enable. False otherwise.
     */
    public boolean getCellularConnectivity() {
        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();

        if (activeInfo != null && activeInfo.isConnected()) {
            mobileConnected = activeInfo.getType() == ConnectivityManager.TYPE_MOBILE;
        } else {
            mobileConnected = false;
        }

        return mobileConnected;
    }

    /**
     * See if the bluetooth adapter is present and then check if is enable.
     * @return (boolean) True if Bluetooth is Enable. False otherwise.
     */
    public boolean getBluetoothConnectivity() {
        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        if (mBluetoothAdapter == null) {
            return false;
        } else if (mBluetoothAdapter.isEnabled()){
            return true;
        } else {
            return false;
        }
    }

    /**
     * Read the available RAM for the system.
     * @return (double) The amount of RAM available for the System.
     */
    public double getAvailableRAM() {
        // RAM reading
        /* refer to: https://developer.android.com/reference/android/app/ActivityManager.MemoryInfo */
        /* The total memory accessible by the kernel. This is basically the RAM size of the device,
            not including below-kernel fixed allocations like DMA buffers, RAM for the baseband CPU, etc.
            The available memory on the system. This number should not be considered absolute: due to the nature of the kernel,
            a significant portion of this memory is actually in use and needed for the overall system to run well. */

        ActivityManager.MemoryInfo myMemoryInfo = new ActivityManager.MemoryInfo();
        ActivityManager activityManager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        activityManager.getMemoryInfo(myMemoryInfo);
        double availMemMB = (double) myMemoryInfo.availMem / MB_CONVERSION;
        //Percentage can be calculated for API 16+ ~ TotalMem return bytes, convert to MBytes.
        double totalMemMB = (double) myMemoryInfo.totalMem / MB_CONVERSION;
        double percentAvail = availMemMB / totalMemMB  * 100.0;

        return percentAvail;
    }

    /**
     * Get the screen current brightness.
     * @return (int) The current brightness of the Screen.
     */
    public int getBrightness() {
        int brightness = Settings.System.getInt(
                getContentResolver(),
                Settings.System.SCREEN_BRIGHTNESS,
                0
        );
        return brightness;
    }

    /**
     * Get as input all the data and transform them to string ready to be save to json file.
     * @return (String) The json to be written.
     */
    public String toJsonString(String userID, int level, float temperature, float voltage, String technology, int status, int health, int usage, boolean bluetooth, boolean wifi, boolean cellular, double RAM, int brightness, int sampleFreq, long timestamp){
        return "{ \"ID\": \"" + userID + "\",\n" +
                " \"level\": " + level + ",\n" +
                " \"temperature\": " + temperature + ",\n" +
                " \"voltage\": " + voltage + ",\n" +
                " \"technology\": \"" + technology + "\",\n" +
                " \"status\": " + status + ",\n" +
                " \"health\": " + health + ",\n" +
                " \"usage\": " + usage + ",\n" +
                " \"WiFi\": \"" + wifi + "\",\n" +
                " \"Cellular\": \"" + cellular + "\",\n" +
                " \"Bluetooth\": \"" + bluetooth + "\",\n" +
                " \"RAM\": " + RAM + ",\n" +
                " \"Brightness\": " + brightness + ",\n" +
                " \"SampleFreq\": " + sampleFreq + ",\n" +
                " \"Timestamp\": " + timestamp + "},";
    }
}

