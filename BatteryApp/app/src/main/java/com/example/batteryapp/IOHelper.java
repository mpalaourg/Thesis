package com.example.batteryapp;

import android.content.Context;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;

public class IOHelper {
    Context fileContext;

    public IOHelper(Context fileContext){
        this.fileContext = fileContext;
    }

    /* Create a file with name "FILE_NAME" that contains "text" */
    public void saveFile(String FILE_NAME, String text) {
        FileOutputStream fos = null;
        try {
            fos = fileContext.openFileOutput(FILE_NAME, Context.MODE_PRIVATE | Context.MODE_APPEND);
            fos.write(text.getBytes());

            //Toast.makeText( fileContext, "Saved to " + fileContext.getFilesDir() + "/" + FILE_NAME, Toast.LENGTH_LONG).show();
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

    /* Read the file from the internal storage and return its content. */
    public String loadFile(String FILE_NAME) {
        FileInputStream fis = null;
        String body = "";
        try {
            fis = fileContext.openFileInput(FILE_NAME);
            InputStreamReader isr = new InputStreamReader(fis);
            BufferedReader br = new BufferedReader(isr);
            StringBuilder sb = new StringBuilder();
            String text;

            while ((text = br.readLine()) != null) {
                sb.append(text).append("\n");
            }
            /* Delete the last ,\n */
            body = sb.toString();
            if (body != null && body.length() > 0){ body = body.substring(0, body.length()-2); }
            body = "[" + body + "]";
            // System.out.println(body);
            // System.out.println(fis.getChannel().size());
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
        return body;
    }

    /* Upload the files and delete them */
    public void deleteFile(){
        String[] files = fileContext.fileList();

        for (String FILE_NAME : files) {
            if ( !FILE_NAME.contains("UUID")) {
                fileContext.deleteFile(FILE_NAME);
            }
        }
    }
}
