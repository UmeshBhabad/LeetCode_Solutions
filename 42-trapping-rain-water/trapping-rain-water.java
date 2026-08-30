class Solution
{
    public int trap(int[] height)
    {
        int n = height.length;

        int totalWater = 0;

        int l = 0, r = n - 1;

        int leftMax = height[l], rightMax = height[r];

        while(l < r)
        {
            

            if(leftMax < rightMax)
            {
                l++;
                leftMax = Math.max(leftMax, height[l]);
                totalWater += leftMax - height[l];
            }
            else
            {
                r--;
                rightMax = Math.max(rightMax, height[r]);;
                totalWater += rightMax - height[r];
            }
        }
        return totalWater;
    }
}