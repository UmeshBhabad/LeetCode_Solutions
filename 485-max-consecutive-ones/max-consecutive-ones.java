class Solution
{
    static
    {
        for(int i = 0; i < 1000; i++)
        {
            findMaxConsecutiveOnes(new int[]{});
        }
    }
    public static int findMaxConsecutiveOnes(int[] nums)
    {
        int n = nums.length;

        int r = 0;

        int count = 0, maxCount = 0;

        while(r < n)
        {
            if(nums[r] == 1)
            {
                count++;
            }
            else
            {
                count = 0;
            }
            maxCount = Math.max(maxCount, count);
            r++;
        }

        return maxCount;
    }
}