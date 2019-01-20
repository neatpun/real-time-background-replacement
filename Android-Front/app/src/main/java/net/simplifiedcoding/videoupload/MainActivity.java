package net.simplifiedcoding.videoupload;

import android.content.Intent;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnPreparedListener;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.text.format.Formatter;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.VideoView;
import cn.jzvd.Jzvd;
import cn.jzvd.JzvdStd;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.RequestQueue.RequestFinishedListener;
import com.android.volley.Response.Listener;
import com.android.volley.toolbox.Volley;
import com.github.tcking.giraffecompressor.GiraffeCompressor;
import com.github.tcking.giraffecompressor.GiraffeCompressor.Result;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import net.simplifiedcoding.videoupload.CustomFileRequestBuilder.ErrorListener;
import net.simplifiedcoding.videoupload.CustomFileRequestBuilder.MultiPartRequest;
import rx.Subscriber;
import rx.android.schedulers.AndroidSchedulers;

public class MainActivity extends AppCompatActivity {

  private static final String TAG = MainActivity.class.getSimpleName() + " YOY";
  private Button buttonChoose;
  private Button buttonUpload;
  private TextView textView;
  private TextView textViewResponse;
  VideoView vv;

  private static final int SELECT_IMG = 3;
  private static final int SELECT_VIDEO2 = 6;

  private Uri selectedImg;
  private Uri mainee;

  DialogProgress dialogProgress;

  File outFile;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    buttonChoose = findViewById(R.id.buttonChoose);
    buttonUpload = findViewById(R.id.buttonUpload);
    vv = findViewById(R.id.vp2);

    findViewById(R.id.buttonVid).setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {
        Log.i(TAG, "onClick: mera");
        Intent i = new Intent(Intent.ACTION_GET_CONTENT);
        i.setType("video/*");
        startActivityForResult(Intent.createChooser(i, "Select a Video "), SELECT_VIDEO2);
      }
    });

    buttonChoose.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {
        chooseImage();
      }
    });

    buttonUpload.setOnClickListener(new OnClickListener() {
      @Override
      public void onClick(View v) {
        uploadVideo();
      }
    });

    vv.setOnPreparedListener(new OnPreparedListener() {
      @Override
      public void onPrepared(MediaPlayer mp) {
        mp.setLooping(true);
      }
    });

    textView = findViewById(R.id.textView);
    textViewResponse = findViewById(R.id.textViewResponse);

    GiraffeCompressor.init(this);

  }

  private void chooseImage() {
    Intent intent = new Intent();
    intent.setType("image/*");
    intent.setAction(Intent.ACTION_GET_CONTENT);
    startActivityForResult(Intent.createChooser(intent, "Select an Image"), SELECT_IMG);
  }

  @Override
  public void onActivityResult(int requestCode, int resultCode, Intent data) {
    if (resultCode == RESULT_OK) {

      if (requestCode == SELECT_IMG) {

        System.out.println("SELECT_IMG");
        selectedImg = data.getData();
        assert selectedImg != null;
        textView.setText(selectedImg.toString());

      } else if (requestCode == SELECT_VIDEO2) {

        Log.i(TAG, "onActivityResult: " + SELECT_VIDEO2);
        mainee = data.getData();
        assert mainee != null;
        textView.setText(mainee.toString());

      } else {
        //
//                Uri selectedImageUri = data.getData();
//                try {
//                    assert selectedImageUri != null;
//
//                    File final_file = new File(selectedImageUri.getPath());
//
//                    MultipartEntity entity = new MultipartEntity();
//                    /* example for adding an image part */
//                    FileBody fileBody = new FileBody(final_file); // image should be
//                    // a String
//                    entity.addPart("file_fg", fileBody);
//
////                    entity.addPart("upload_medium", new StringBody("direct"));
////
////                    entity.addPart("file_name", new StringBody("Taj Mahal"));
//
//                    Volley.newRequestQueue(MainActivity.this).add(
//                    new CustomMultipartRequest(Config.UPLOAD_URL, new Response.ErrorListener() {
//                        @Override
//                        public void onErrorResponse(VolleyError error) {
//                            Log.e(TAG, "onErrorResponse: ",error );
//                        }
//                    }, new Listener<String>() {
//                        @Override
//                        public void onResponse(String response) {
//                            Log.i(TAG, "onResponse: "+ response);
//                        }
//                    }, entity)
//                    );

//                }catch (NoSuchMethodError e){
//                    e.printStackTrace();
//                }
      }
    }
  }


  private void uploadVideo() {

    if (mainee != null) {
      Log.i(TAG, "uploadVideo: start");

//      compress(mainee);

      dialogProgress = DialogProgress.newInstance("Processing Video...");
      dialogProgress.setCancelable(false);
      dialogProgress.display(MainActivity.this);

      CustomFileRequestBuilder builder = new CustomFileRequestBuilder(MainActivity.this, new Listener<byte[]>() {
        @Override
        public void onResponse(byte[] response) {
          Toast.makeText(MainActivity.this, "Done.", Toast.LENGTH_SHORT).show();
          if (response != null) {

            class SavePhotoTask extends AsyncTask<byte[], String, File> {

              @Override
              protected void onPreExecute() {
                Log.i(TAG, "onPreExecute: ");
                super.onPreExecute();
              }

              @Override
              protected File doInBackground(byte[]... jpeg) {
                File photo = new File(Environment.getExternalStorageDirectory(), System.currentTimeMillis() + ".mp4");

                try {
                  if (photo.exists()) {
                    photo.delete();
                  }
                  photo.createNewFile();

                  try {
                    FileOutputStream fos = new FileOutputStream(photo.getPath());

                    fos.write(jpeg[0]);
                    fos.close();
                  } catch (IOException e) {
                    Log.e("PictureDemo", "Exception in photoCallback", e);
                  }
                } catch (IOException e) {
                  e.printStackTrace();
                }

                return (photo);
              }

              @Override
              protected void onPostExecute(File s) {
                super.onPostExecute(s);
                outFile = s;
                vv.setVideoURI(Uri.fromFile(outFile));
                vv.start();
                Log.i(TAG, "onPostExecute: "+s.getPath());
              }
            }

            new SavePhotoTask().execute(response);

            dialogProgress.setCancelable(true);
            dialogProgress.dismiss();

            Log.i(TAG, "onResponse: complete");
            Toast.makeText(MainActivity.this, "Download complete.", Toast.LENGTH_LONG).show();

          } else {
            Log.i(TAG, "onResponse: null");
          }
        }
      }, new ErrorListener() {
        @Override
        public void onError(String err) {
          Log.e(TAG, "onError: " + err);
          Toast.makeText(MainActivity.this, "Error: "+err, Toast.LENGTH_SHORT).show();
          dialogProgress.setCancelable(true);
          dialogProgress.dismiss();
        }
      });
      builder.addUri(mainee, 1).build();
      if (selectedImg != null) {
        builder.addUri(selectedImg, 0);
      }

      MultiPartRequest request = builder.build();

      request.setRetryPolicy(new DefaultRetryPolicy(
          5 * 60 * 1000,
          DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
          DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));

      request.setShouldCache(false);

      RequestQueue requestQueue = Volley.newRequestQueue(MainActivity.this);
      requestQueue.add(request);
      requestQueue.addRequestFinishedListener(new RequestFinishedListener<Object>() {
        @Override
        public void onRequestFinished(Request<Object> request) {
          Log.i(TAG, "onRequestFinished: ");
        }
      });
      Log.i(TAG, "uploadVideo: added");

    } else {
      Toast.makeText(this, "Please select a video first", Toast.LENGTH_SHORT).show();
    }
  }

  private void compress(Uri u) {

    GiraffeCompressor.create() //two implementations: mediacodec and ffmpeg,default is mediacodec
        .input(new File(u.getPath())) //set video to be compressed
//        .output(outputFile) //set compressed video output
//        .bitRate(bitRate)//set bitrate 码率
//        .resizeFactor( 0.5 )//set video resize factor 分辨率缩放,默认保持原分辨率
        .watermark("/sdcard/videoCompressor/watermarker.png")//add watermark(take a long time) 水印图片(需要长时间处理)
        .ready()
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe(new Subscriber<Result>() {
          @Override
          public void onCompleted() {
            Log.i(TAG, "onCompleted: ");
          }

          @Override
          public void onError(Throwable e) {
            e.printStackTrace();
            Log.i(TAG, "onError: ", e);
          }

          @Override
          public void onNext(GiraffeCompressor.Result s) {
            String msg = String.format("compress completed \ntake time:%s \nout put file:%s", s.getCostTime(), s.getOutput());
//            msg = msg + "\ninput file size:"+ Formatter.formatFileSize(getApplication(),inputFile.length());
            msg = msg + "\nout file size:" + Formatter.formatFileSize(getApplication(), new File(s.getOutput()).length());
            System.out.println(msg);
//            $.id(R.id.tv_console).text(msg);
          }
        });

  }

  @Override
  public void onBackPressed() {
    if (Jzvd.backPress()) {
      return;
    }
    super.onBackPressed();
  }

  @Override
  protected void onPause() {
    super.onPause();
    Jzvd.releaseAllVideos();
  }

  /*
  class UploadVideo extends AsyncTask<Void, Void, String> {

      ProgressDialog uploading;

      @Override
      protected void onPreExecute() {
        super.onPreExecute();
        uploading = ProgressDialog.show(MainActivity.this, "Uploading File", "Please wait...", false, false);
      }

      @Override
      protected void onPostExecute(String s) {
        super.onPostExecute(s);
        uploading.dismiss();
        textViewResponse.setText(Html.fromHtml("<b>Uploaded at <a href='" + s + "'>" + s + "</a></b>"));
        textViewResponse.setMovementMethod(LinkMovementMethod.getInstance());
      }

      @Override
      protected String doInBackground(Void... params) {
        Upload u = new Upload();
        String msg = u.upLoad2Server(selectedImg);
        return msg;
      }
    }
    UploadVideo uv = new UploadVideo();
      uv.execute();
  public String getPath(Uri uri) {
    Cursor cursor = getContentResolver().query(uri, null, null, null, null);
    cursor.moveToFirst();
    String document_id = cursor.getString(0);
    document_id = document_id.substring(document_id.lastIndexOf(":") + 1);
    cursor.close();

    cursor = getContentResolver().query(
        android.provider.MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
        null, MediaStore.Images.Media._ID + " = ? ", new String[]{document_id}, null);
    cursor.moveToFirst();
    String path = cursor.getString(cursor.getColumnIndex(MediaStore.Video.Media.DATA));
    cursor.close();

    return path;
  }
  */
}
