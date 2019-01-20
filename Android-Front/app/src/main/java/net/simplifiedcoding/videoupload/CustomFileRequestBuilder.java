package net.simplifiedcoding.videoupload;

import android.Manifest.permission;
import android.content.ContentResolver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.DialogInterface.OnClickListener;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Rect;
import android.net.Uri;
import android.support.v4.app.ActivityCompat;
import android.support.v4.util.Pair;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import cn.jzvd.JzvdStd;
import com.android.volley.AuthFailureError;
import com.android.volley.NetworkResponse;
import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.HttpHeaderParser;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class CustomFileRequestBuilder {

  private static final String TAG = CustomFileRequestBuilder.class.getSimpleName() + " YOYO";

  private static final String URL_Img_Upload = Config.UPLOAD_URL;

  private Context context;
  private ArrayList<Pair<Uri, Integer>> uris;
  private Response.Listener<byte[]> successListener;
  private ErrorListener errorListener;
  private String token;


  private CustomFileRequestBuilder() {
  }

  public CustomFileRequestBuilder(Context context, Response.Listener<byte[]> successListener, ErrorListener errorListener) {
    this.context = context;
    this.successListener = successListener;
    this.errorListener = errorListener;
  }

  public MultiPartRequest build() {
    return new MultiPartRequest(Request.Method.POST, errorListener);
  }

  public CustomFileRequestBuilder setToken(String token) {
    this.token = token;
    return this;
  }

  public CustomFileRequestBuilder addUri(Uri uri, int type) {
    if (uris == null) {
      uris = new ArrayList<>();
    }
    uris.add(new Pair<>(uri, type));
    return this;
  }

  public class MultiPartRequest extends Request<byte[]> {

    private final String twoHyphens = "--";
    private final String lineEnd = "\r\n";
    private final String boundary = "apiclient-" + System.currentTimeMillis();

    private MultiPartRequest(int method, final ErrorListener errorListener) {
      super(method, URL_Img_Upload, new Response.ErrorListener() {
        @Override
        public void onErrorResponse(VolleyError error) {
          String err = error.getMessage();
          if (error.networkResponse != null) {
            if (error.networkResponse.data != null) {
              err = new String(error.networkResponse.data, StandardCharsets.UTF_8);
              err = "code: " + error.networkResponse.statusCode + " body: " + err;
            }
          }
          errorListener.onError(err);
        }
      });
    }

    @Override
    public Map<String, String> getHeaders() {
      Map<String, String> headers = new HashMap<>();
      headers.put("Accept", "application/json");
      headers.put("Authorization", "Bearer " + token);
//            headers.put("Content-Type", "multipart/form-data");
      return headers;
    }

    @Override
    public String getBodyContentType() {
      return "multipart/form-data;boundary=" + boundary;
    }

    @Override
    public byte[] getBody() throws AuthFailureError {

      ByteArrayOutputStream bos = new ByteArrayOutputStream();
      DataOutputStream dos = new DataOutputStream(bos);

      try {

        // populate text payload
        Map<String, String> params = getParams();
        if (params != null && params.size() > 0) {
          addTextPart(dos, params, getParamsEncoding());
        }

        // populate data byte payload
        Map<String, DataPart> data = getDataPayload();
        if (data != null && data.size() > 0) {
          addDataParts(dos, data);
        }

        // close multipart form data after text and file data
        dos.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

        return bos.toByteArray();
      } catch (IOException e) {
        e.printStackTrace();
//        errorListener.onError(e.getMessage());
//        cancel();
//        deliverError(new VolleyError());
      }
      return null;

    }

    @Override
    protected Response<byte[]> parseNetworkResponse(NetworkResponse response) {
      try {
        String id = new String(
            response.data,
            HttpHeaderParser.parseCharset(response.headers));
        Log.i(TAG, "parseNetworkResponse: "+id);
      } catch (UnsupportedEncodingException e) {
        e.printStackTrace();
      }
      return Response.success(response.data, HttpHeaderParser.parseCacheHeaders(response));
    }

    @Override
    protected void deliverResponse(byte[] response) {
      successListener.onResponse(response);
    }

    private Map<String, DataPart> getDataPayload() throws IOException {
      Map<String, DataPart> params = new HashMap<>();
      for (Pair<Uri, Integer> p: uris) {

        if(p.second==0){
          String imageName = System.currentTimeMillis() + ".jpeg";
          byte[] bytes = convertImageToByte2(p.first);
          if (bytes == null) {
            throw new IOException();
          }
          DataPart dataPart = new DataPart(imageName, bytes);
          dataPart.setType("image/jpeg");
          params.put("file_bg", dataPart);

        }else {
          String vidName = System.currentTimeMillis() + ".mp4";
          byte[] bytes = convertVideoToByte(p.first);
          if (bytes == null) {
            throw new IOException();
          }
          DataPart dataPart = new DataPart(vidName, bytes);
          dataPart.setType("video/mp4");
          params.put("file_fg", dataPart);
        }

      }
      return params;
    }

    private void addTextPart(DataOutputStream dataOutputStream, Map<String, String> params,
        String encoding) throws IOException {
      try {
        for (Map.Entry<String, String> entry : params.entrySet()) {

          dataOutputStream.writeBytes(twoHyphens + boundary + lineEnd);
          dataOutputStream
              .writeBytes("Content-Disposition: form-data; name=\"" + entry.getKey() + "\"" + lineEnd);
          dataOutputStream.writeBytes(lineEnd);
          dataOutputStream.writeBytes(entry.getValue() + lineEnd);

        }
      } catch (UnsupportedEncodingException uee) {
        throw new RuntimeException("Encoding not supported: " + encoding, uee);
      }
    }


    private void addDataParts(DataOutputStream dataOutputStream, Map<String, DataPart> data)
        throws IOException {
      for (Map.Entry<String, DataPart> entry : data.entrySet()) {
        buildDataPart(dataOutputStream, entry.getValue(), entry.getKey());
      }
    }

    private void buildDataPart(DataOutputStream dataOutputStream, DataPart dataFile,
        String inputName) throws IOException {

      dataOutputStream.writeBytes(twoHyphens + boundary + lineEnd);
      dataOutputStream.writeBytes("Content-Disposition: form-data; name=\"" +
          inputName + "\"; filename=\"" + dataFile.getFileName() + "\"" + lineEnd);
      if (dataFile.getType() != null && !dataFile.getType().trim().isEmpty()) {
        dataOutputStream.writeBytes("Content-Type: " + dataFile.getType() + lineEnd);
      }
      dataOutputStream.writeBytes(lineEnd);

      ByteArrayInputStream fileInputStream = new ByteArrayInputStream(dataFile.getContent());
      int bytesAvailable = fileInputStream.available();

      int maxBufferSize = 1024 * 1024;
      int bufferSize = Math.min(bytesAvailable, maxBufferSize);
      byte[] buffer = new byte[bufferSize];

      int bytesRead = fileInputStream.read(buffer, 0, bufferSize);

      while (bytesRead > 0) {
        dataOutputStream.write(buffer, 0, bufferSize);
        bytesAvailable = fileInputStream.available();
        bufferSize = Math.min(bytesAvailable, maxBufferSize);
        bytesRead = fileInputStream.read(buffer, 0, bufferSize);
      }

      dataOutputStream.writeBytes(lineEnd);

    }

    private byte[] convertImageToByte(Uri uri) {
      byte[] data = null;
      try {
        ContentResolver cr = context.getContentResolver();
        InputStream inputStream = cr.openInputStream(uri);

        Bitmap bitmap = BitmapFactory.decodeStream(inputStream);
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, baos);
        data = baos.toByteArray();
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      }
      return data;
    }

    private byte[] convertImageToByte2(Uri uri) {
      byte[] data = null;
      try {

        ContentResolver cr = context.getContentResolver();
        InputStream inputStream = cr.openInputStream(uri);

        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inJustDecodeBounds = true;
        BitmapFactory.decodeStream(inputStream, null, options);

        // Calculate inSampleSize
        options.inSampleSize = calculateInSampleSize(options);

        // Decode bitmap with inSampleSize set
        options.inJustDecodeBounds = false;

        InputStream inputStream2 = cr.openInputStream(uri);
        Bitmap bitmap = BitmapFactory.decodeStream(inputStream2, new Rect(0, 0, 0, 0), options);

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, 70, baos);
        data = baos.toByteArray();

      } catch (FileNotFoundException e) {
        e.printStackTrace();
      } catch (SecurityException e) {
        e.printStackTrace();

        final AppCompatActivity activity = (AppCompatActivity) CustomFileRequestBuilder.this.context;

        if (ActivityCompat.shouldShowRequestPermissionRationale(activity,
            permission.READ_EXTERNAL_STORAGE)) {

          new AlertDialog.Builder(context)
              .setTitle("Need File Permission")
              .setMessage("To upload your picture we need you need to give us access to your images first")
              .setPositiveButton("Ok", new OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                  ActivityCompat.requestPermissions(activity,
                      new String[]{permission.READ_EXTERNAL_STORAGE},
                      7);
                }
              }).create().show();

        } else {

          ActivityCompat.requestPermissions(activity,
              new String[]{permission.READ_EXTERNAL_STORAGE},
              7);

        }

      }
      return data;
    }

    private byte[] convertVideoToByte(Uri uri) {

      ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
      try {
        InputStream iStream = context.getContentResolver().openInputStream(uri);
        int bufferSize = 2048;
        byte[] buffer = new byte[bufferSize];

        // we need to know how may bytes were read to write them to the byteBuffer
        int len = 0;
        if (iStream != null) {
          while ((len = iStream.read(buffer)) != -1) {
            byteArrayOutputStream.write(buffer, 0, len);
          }
        }
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      } catch (IOException e) {
        e.printStackTrace();
      }

      return byteArrayOutputStream.toByteArray();
    }

    private int calculateInSampleSize(BitmapFactory.Options options) {

      int actualWidth = options.outWidth;
      int actualHeight = options.outHeight;

      float imgRatio = actualWidth / actualHeight;
      float maxRatio = 16 / 9;

      int maxWidth = 1200;
      int maxHeight = (int) (maxWidth / maxRatio);

      // width and height values are set maintaining the aspect ratio of the image

      if (actualHeight > maxHeight || actualWidth > maxWidth) {
        if (imgRatio < maxRatio) {
          imgRatio = maxHeight / actualHeight;
          actualWidth = (int) (imgRatio * actualWidth);
          actualHeight = maxHeight;
        } else if (imgRatio > maxRatio) {
          imgRatio = maxWidth / actualWidth;
          actualHeight = (int) (imgRatio * actualHeight);
          actualWidth = maxWidth;
        } else {
          actualHeight = maxHeight;
          actualWidth = maxWidth;

        }
      }
      int reqWidth = actualWidth;
      int reqHeight = actualHeight;

      // Raw height and width of image
      final int height = options.outHeight;
      final int width = options.outWidth;
      int inSampleSize = 1;

      if (height > reqHeight || width > reqWidth) {

        final int halfHeight = height / 2;
        final int halfWidth = width / 2;

        // Calculate the largest inSampleSize value that is a power of 2 and keeps both
        // height and width larger than the requested height and width.
        while ((halfHeight / inSampleSize) >= reqHeight && (halfWidth / inSampleSize) >= reqWidth) {
          inSampleSize *= 2;
        }
      }

      return inSampleSize;
    }

    public class DataPart {

      private String fileName;
      private byte[] content;
      private String type;

      public DataPart() {
      }

      public DataPart(String name, byte[] data) {
        fileName = name;
        content = data;
      }

      String getFileName() {
        return fileName;
      }

      byte[] getContent() {
        return content;
      }

      String getType() {
        return type;
      }

      public void setType(String type) {
        this.type = type;
      }

    }

  }

  public interface ErrorListener {

    void onError(String err);
  }

}