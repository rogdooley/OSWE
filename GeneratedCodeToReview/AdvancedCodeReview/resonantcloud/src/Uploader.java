import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;

import java.io.File;

public class Uploader {
    public static void main(String[] args) {
        AmazonS3 s3 = AmazonS3ClientBuilder.standard()
                .withCredentials(new ProfileCredentialsProvider("default"))
                .withRegion("us-east-1")
                .build();

        String bucket = "resonant-logs";
        String path = args.length > 0 ? args[0] : "secret_dump.txt";
        File file = new File(path);

        if (!file.exists()) {
            System.out.println("File not found");
            return;
        }

        s3.putObject(bucket, file.getName(), file);
        System.out.println("Uploaded to bucket: " + bucket);
    }
}
