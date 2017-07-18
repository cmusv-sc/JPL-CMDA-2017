function [ha, cb] = displayTwoDimData(lon, lat, twoDimData, ha, cfgParams)
%
% This function displays two dimensional data (longitude x latitude)
% overlaying on top of a coastal line.
%
persistent coastData;

if isempty(coastData)
  coastLongAndLat = load([getDataDirectory('displayTwoDimData') '/coastLineData.txt']);
  coastLongAndLat = reshape(coastLongAndLat, [], 2);
end

if nargin < 5
if nargin < 4
figure;
ha = gca;
end
xlabelOff = false;
ylabelOff = false;
else
  xlabelOff = cfgParams.xlabelOff;
  ylabelOff = cfgParams.ylabelOff;
end
imagesc(lon, -lat, twoDimData');
colorLim = determineDisplayRange(twoDimData(:));
caxis(colorLim);

crossingZero = prod(colorLim) < 0;

if isfield(cfgParams, 'logScale')
  crossingZero = ~cfgParams.logScale;
end

if crossingZero
  cmap = myColorMap(colorLim, 'lin0');
else
  cmap = colormap('jet');
end

if ~isempty(find(isnan(twoDimData(:))))
  cmap(1,:) = [1,1,1] * double(~crossingZero);
end

colormap(cmap);
cb=colorbar('southoutside');

hold on;
plot(ha, coastLongAndLat(:,2)-360, -coastLongAndLat(:,1), 'k-');
plot(ha, coastLongAndLat(:,2), -coastLongAndLat(:,1), 'k-');
plot(ha, coastLongAndLat(:,2)+360, -coastLongAndLat(:,1), 'k-');
set(ha, 'fontsize', 13, 'fontweight', 'bold');
set(ha, 'yTickLabel', num2strNoNegZero(-get(gca, 'yTick')'));
if ~xlabelOff
  xlabel(ha, 'longitude(deg)');
end
if ~ylabelOff
  ylabel(ha, 'latitude(deg)');
end
