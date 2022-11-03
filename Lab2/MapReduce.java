import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class MapReduce {
    static public class FriendCountWritable implements Writable {
        public Long user;
        public Long mutualFriend;

        public FriendCountWritable(Long user, Long mutualFriend) {
            this.user = user;
            this.mutualFriend = mutualFriend;
        }

        public FriendCountWritable() {
            this(-1L, -1L);
        }

        @Override
        public void write(DataOutput out) throws IOException {
            out.writeLong(user);
            out.writeLong(mutualFriend);
        }

        @Override
        public void readFields(DataInput in) throws IOException {
            user = in.readLong();
            mutualFriend = in.readLong();
        }

        @Override
        public String toString() {
            return " toUser: "
                    + Long.toString(user) + " mutualFriend: " + Long.toString(mutualFriend);
        }
    }
    public static class TokenizerMapper extends Mapper<LongWritable, Text, LongWritable, FriendCountWritable>{
        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String[] line = value.toString().split("\t");
            Long currUser = Long.parseLong(line[0]);
            List<Long> friendsIdsParsed = new ArrayList<Long>();

            if (line.length == 2) { // if the list of friends is not empty
                String[] friendsIds = line[1].split(",");
                for (String friendId : friendsIds) {
                    Long friendIdParsed = Long.parseLong(friendId);
                    friendsIdsParsed.add(friendIdParsed);
                    context.write(new LongWritable(currUser), new FriendCountWritable(friendIdParsed, -1L));
                }

                for (int i = 0; i < friendsIdsParsed.size(); i++) {
                    for (int j = i + 1; j < friendsIdsParsed.size(); j++) {
                        // for each current user friends combination, set currentUser as mutual friend to both
                        context.write(new LongWritable(friendsIdsParsed.get(i)), new FriendCountWritable((friendsIdsParsed.get(j)), currUser));
                        context.write(new LongWritable(friendsIdsParsed.get(j)), new FriendCountWritable((friendsIdsParsed.get(i)), currUser));
                    }
                }
            }
        }
    }

    public static class IntSumReducer extends Reducer<LongWritable, FriendCountWritable, LongWritable, Text> {
        @Override
        public void reduce(LongWritable key, Iterable<FriendCountWritable> values, Context context)
                throws IOException, InterruptedException {

            // key is the recommended friend, and value is the list of mutual friends
            final java.util.Map<Long, List<Long>> mutualFriendsRecommendedFriend = new HashMap<Long, List<Long>>();

            for (FriendCountWritable val : values) {
                final boolean alreadyFriend = (val.mutualFriend == -1);
                final long currPotentialFriend = val.user;
                final long mutualFriend = val.mutualFriend;

                final boolean currPotentialFriendAlreadyTreated = mutualFriendsRecommendedFriend.containsKey(currPotentialFriend);

                if (currPotentialFriendAlreadyTreated) {
                    if (alreadyFriend) {
                        mutualFriendsRecommendedFriend.put(currPotentialFriend, null);
                        continue;
                    }
                    if (mutualFriendsRecommendedFriend.get(currPotentialFriend) != null) {
                        mutualFriendsRecommendedFriend.get(currPotentialFriend).add(mutualFriend);

                    }
                    continue;
                }
                if (!alreadyFriend) {
                    mutualFriendsRecommendedFriend.put(currPotentialFriend,
                            new ArrayList<Long>() {{add(mutualFriend);}}
                    );
                } else {
                    mutualFriendsRecommendedFriend.put(currPotentialFriend, null);
                }

            }

            java.util.SortedMap<Long, List<Long>> sortedMutualFriends = new TreeMap<Long, List<Long>>(new Comparator<Long>() {
                @Override
                public int compare(Long key1, Long key2) {
                    Integer v1 = mutualFriendsRecommendedFriend.get(key1).size();
                    Integer v2 = mutualFriendsRecommendedFriend.get(key2).size();
                    if (v1 > v2) {
                        return -1;
                    } else if (v1.equals(v2) && key1 < key2) {
                        return -1;
                    } else {
                        return 1;
                    }
                }
            });

            for (java.util.Map.Entry<Long, List<Long>> entry : mutualFriendsRecommendedFriend.entrySet()) {
                if (entry.getValue() != null) {
                    sortedMutualFriends.put(entry.getKey(), entry.getValue());
                }
            }

            int i = 0;
            String output = "";
            for (java.util.Map.Entry<Long, List<Long>> entry : sortedMutualFriends.entrySet()) {
                if (i == 0) {
                    output = entry.getKey().toString();
                } else {
                    output += "," + entry.getKey().toString();
                }
                ++i;
            }
            context.write(key, new Text(output));
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "word count");
        job.setJarByClass(MapReduce.class);
        job.setMapperClass(TokenizerMapper.class);
        // job.setCombinerClass(IntSumReducer.class);
        job.setReducerClass(IntSumReducer.class);
        job.setMapOutputKeyClass(LongWritable.class);
        job.setMapOutputValueClass(FriendCountWritable.class);
        job.setOutputKeyClass(LongWritable.class);
        job.setOutputValueClass(Text.class);
        
        FileSystem outFs = new Path(args[1]).getFileSystem(conf);
        outFs.delete(new Path(args[1]), true);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}