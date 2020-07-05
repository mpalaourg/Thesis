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
import android.location.LocationManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.WifiManager;
import android.os.BatteryManager;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import android.provider.Settings;

import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Timer;
import java.util.TimerTask;

public class MyService extends Service {
    private String userID, FILE_NAME;

    private Timer timer;
    private CPU_Info myCPUInfo;
    private Battery_Receiver myBroadcast ;
    private IOHelper myIOHelper;
    private LocalBroadcastManager broadcaster;
    private PowerManager.WakeLock wl;
    private PowerManager pm;
    private int level = 0, status, health, availCapacity;
    private float temperature = 0.0f, voltage = 0.0f;
    private String technology, brandModel, androidVersion;
    private boolean bluetooth, wifi, cellular, hotspot, GPS, isInteractive;
    private double  RAM;
    private int     usage, brightness, sampleFreq;
    private long    timestamp;

    /** Function which is called at the creation of the Service. First, initialize class variables.
     * Then a partial WakeLock will be acquired, to prevent the DOZE Mode to effect the sampling of
     * the Service. A receiver will be register to wait for "ACTION_BATTERY_CHANGED" intents. Finally,
     * for androids version after O will a create a foreground service with a notification, where the
     * proper notification channel is initialized. Otherwise, the service has a simple notification.
     */
    @Override
    public void onCreate() {
        super.onCreate();
        timer = new Timer();
        myCPUInfo = new CPU_Info();
        myBroadcast  = new Battery_Receiver();
        myIOHelper = new IOHelper(this);
        broadcaster = LocalBroadcastManager.getInstance(this);
        pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        /* Ref Link: https://stackoverflow.com/a/29006964 && https://www.androiddesignpatterns.com/2013/08/binders-death-recipients.html
         If process will be killed, the WakeLock will be released */
        wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "BatteryApp:SamplingVariablesWakelock");
        wl.acquire();

        registerBatteryLevelReceiver();

        if (Build.VERSION.SDK_INT > Build.VERSION_CODES.O)
            startMyOwnForeground();
        else
            startForeground(1, new Notification());
    }

    /**
     * This method will be called on the start of the service. First, the variables known to be const
     * while the service is running will be initialized. Then, a TimerTask will be scheduled to run
     * periodically every 'sampleFreq' seconds. At each run, the battery stats will be sampled from
     * the BroadcastReceiver*, the connectivity stats will be sampled from the System and the same for
     * the current brightness and RAM Available. Finally, at the end of the runs 'UpdateIntent' intents
     * will be sent to the UI Thread and append the new json formatted sample to the file of the current session.
     * *updated at each 'ACTION_BATTERY_CHANGED' intent
     *
     * @param intent  -> The Intent supplied to Context.startService(Intent), as given.
     * @param flags   -> Additional data about this start request. Value is either 0 or a combination of START_FLAG_REDELIVERY, and START_FLAG_RETRY
     * @param startId -> A unique integer representing this specific request to start.
     * @return The return value indicates what semantics the system should use for the service's current started state.
     */
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        brandModel = Build.BRAND + "-" + Build.MODEL;
        androidVersion = Build.VERSION.RELEASE;
        sampleFreq = intent.getIntExtra("SampleFreq", 10);
        userID     = intent.getStringExtra("userID");
        FILE_NAME  = intent.getStringExtra("FILENAME");

        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                timestamp = System.currentTimeMillis();
                usage     = getCPUUsage();

                level         = myBroadcast.getLevel();
                status        = myBroadcast.getStatus();
                health        = myBroadcast.getHealth();
                temperature   = myBroadcast.getTemperature();
                voltage       = myBroadcast.getVoltage();
                technology    = myBroadcast.getTechnology();
                availCapacity = getRemainingCapacityPercentage();

                wifi          = getWiFiConnectivity();
                cellular      = getCellularConnectivity();
                bluetooth     = getBluetoothConnectivity();
                hotspot       = getWiFiTetheringConnectivity();
                GPS           = checkGPSEnabled();
                RAM           = Math.round( getAvailableRAM() * 100.0) / 100.0;
                isInteractive = pm.isInteractive();
                brightness    = getBrightness(isInteractive);

                /* Send the intent to update the UI */
                Intent updateIntent = new Intent("UpdateIntent");
                updateIntent.putExtra("WiFiConnectivity", wifi);
                updateIntent.putExtra("CellularConnectivity", cellular);
                updateIntent.putExtra("BluetoothConnectivity", bluetooth);
                updateIntent.putExtra("AvailableRAM", RAM);
                updateIntent.putExtra("Brightness", brightness);
                updateIntent.putExtra("CPU", usage);

                updateIntent.putExtra("BatteryLevel", level);
                updateIntent.putExtra("BatteryStatus", myBroadcast.getStatusString(status) );
                updateIntent.putExtra("BatteryHealth", myBroadcast.getHealthString(health) );
                updateIntent.putExtra("BatteryTemp", temperature);
                updateIntent.putExtra("BatteryVolt", voltage);
                updateIntent.putExtra("BatteryTech", technology);
                updateIntent.putExtra("BatteryUpdateDate", myBroadcast.getDate());
                broadcaster.sendBroadcast(updateIntent);

                String json = toJsonString(userID, level, temperature, voltage, technology, status, health, usage, bluetooth, wifi, cellular, hotspot,
                                            GPS, RAM, brightness, isInteractive, sampleFreq, brandModel, androidVersion, availCapacity, timestamp);
                System.out.println(timestamp);
                myIOHelper.saveFile(FILE_NAME, json);

            }
        }, 0, sampleFreq * 1000);
        // return START_NOT_STICKY;
        return START_STICKY;
    }

    /** Function which is called before the Service exit and close. Clean up business must be done here.
     *      The Battery BroadcastReceiver must be unregistered.
     *      The WakeLock must be released.
     *      The timer must be cancelled.
     *  Then, the service will be removed from the foreground state [ stopForeground(true) ] and
     *  finally stop running [ stopSelf() ].
     *
     *  When the onDestroy won't be called (i.e Force Stop, the system needs RAM), the process is
     *  gone and so there is no receiver to unregister, timer to be cancelled and wakeLock to be
     *  released. All of that will be gone and Android will take care of them.
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

    /**
     * This method will be called when the app will be swiped from the recent apps. The same applies
     * as onDestroy method.
     *
     * If onDestroy was called before the method does nothing.
     *  - stopSelf() = Stop the service, if it was previously started.
     *  - stopForeground() tries to close the service. If already done, its ok.
     *  - Stacking calls on timer.cancel() have no effect.
     *
     * @param rootIntent -> The original root Intent that was used to launch the task that is being removed.
     */
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
     *
     * @param intent -> The Intent that was used to bind to this service.
     * @return Return the communication channel to the service. Here, null (no binding needed)
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
        return (int) myCPUInfo.readCpuPercentNow();
    }

    /**
     * Check if the WiFi is enable.
     * @return (boolean) True if Wifi is Enable. False otherwise.
     */
    public boolean getWiFiConnectivity() {
        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeInfo = connMgr.getActiveNetworkInfo();

        // Whether there is a Wi-Fi connection.
        boolean wifiConnected;
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

        // Whether there is a mobile connection.
        boolean mobileConnected;
        if (activeInfo != null && activeInfo.isConnected()) {
            mobileConnected = activeInfo.getType() == ConnectivityManager.TYPE_MOBILE;
        } else {
            mobileConnected = false;
        }

        return mobileConnected;
    }

    /**
     * Get via reflection if network tethering (hotspot) is enable.
     * @return (boolean) True if Tethering is Enable. False otherwise.
     */
    public boolean getWiFiTetheringConnectivity() {
        boolean isSuccess = false;
        WifiManager tempWifi = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        try {
            final Method method = tempWifi.getClass().getDeclaredMethod("isWifiApEnabled");
            method.setAccessible(true); //in the case of visibility change in future APIs
            isSuccess = (boolean) method.invoke(tempWifi);
        } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }

        return isSuccess;
    }

    /**
     * See if the bluetooth adapter is present and then check if is enable.
     * @return (boolean) True if Bluetooth is Enable. False otherwise.
     */
    public boolean getBluetoothConnectivity() {
        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        if (mBluetoothAdapter == null) {
            return false;
        } else return mBluetoothAdapter.isEnabled();
    }

    /**
     * See if the GPS is enabled or disabled.
     * @return (boolean) True if GPS Provider is Enable. False otherwise.
     */
    public boolean checkGPSEnabled() {
        LocationManager lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        return lm.isProviderEnabled(LocationManager.GPS_PROVIDER);
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
        int MB_CONVERSION = 1000 * 1000;
        double availMemMB = (double) myMemoryInfo.availMem / MB_CONVERSION;
        // Percentage can be calculated for API 16+ ~ TotalMem return bytes, convert to MBytes.
        double totalMemMB = (double) myMemoryInfo.totalMem / MB_CONVERSION;

        return availMemMB / totalMemMB  * 100.0;
    }

    /**
     * Get the screen current brightness. If screen is interactive, read the current brightness.
     * Otherwise current brightness is 0.
     * @return (int) The current brightness of the Screen.
     */
    public int getBrightness(boolean isInteractive) {
        if (isInteractive) {
            return Settings.System.getInt(
                    getContentResolver(),
                    Settings.System.SCREEN_BRIGHTNESS,
                    0 );
        } else {
            return 0;
        }
    }

    /**
     * Get the remaining battery capacity as a percentage.
     * @return the remaining battery capacity as an int percentage.
     */
    public int getRemainingCapacityPercentage() {
        BatteryManager mBatteryManager = (BatteryManager) getSystemService(Context.BATTERY_SERVICE);
        int capacityPercentage = mBatteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
        if(capacityPercentage == Integer.MIN_VALUE)
            return 0;

        return capacityPercentage;
    }

    /**
     * Get as input all the data and transform them to string ready to be save to json file.
     * @return (String) The json to be written.
     */
    public String toJsonString(String userID, int level, float temperature, float voltage, String technology, int status, int health, int usage,
                               boolean bluetooth, boolean wifi, boolean cellular, boolean hotspot, boolean GPS, double RAM, int brightness, boolean isInteractive,
                               int sampleFreq, String brandModel, String androidVersion, int availCapacity, long timestamp){
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
                " \"Hotspot\": \"" + hotspot + "\",\n" +
                " \"GPS\": \"" + GPS + "\",\n" +
                " \"Bluetooth\": \"" + bluetooth + "\",\n" +
                " \"RAM\": " + RAM + ",\n" +
                " \"Brightness\": " + brightness + ",\n" +
                " \"isInteractive\": \"" + isInteractive + "\",\n" +
                " \"SampleFreq\": " + sampleFreq + ",\n" +
                " \"brandModel\": \"" + brandModel + "\",\n" +
                " \"androidVersion\": \"" + androidVersion + "\",\n" +
                " \"availCapacityPercentage\": " + availCapacity + ",\n" +
                " \"Timestamp\": " + timestamp + "},";
    }
}

